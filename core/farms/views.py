from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, reverse
from django.views.generic.base import View
from django_celery_results.models import TaskResult
from ipware import get_client_ip
from ipware.utils import is_valid_ipv6
from rest_framework import generics
from rest_framework.exceptions import APIException
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import (
    CreateSiteForm,
    CoordinatorSetupSelectForm,
    CoordinatorSetupRegistrationForm,
)
from .models import Site, Coordinator, Controller, MqttMessage
from .serializers import (
    CoordinatorPingSerializer,
    CoordinatorSerializer,
    ControllerSerializer,
    ControllerPingGetSerializer,
    ControllerPingPostSerializer,
    SiteSerializer,
    MqttMessageSerializer,
)


class ExternalIPAddressNotRoutable(APIException):
    status_code = 400
    default_code = "external_ip_address_not_routable"

    def __init__(self, ip_address):
        detail = "External IP address is not routable: {}".format(ip_address)
        super().__init__(detail=detail)


class ExternalIPAddressV6(APIException):
    status_code = 400
    default_code = "external_ip_address_v6"

    def __init__(self, ip_address):
        detail = "External IPv6 address is not supported: {}".format(ip_address)
        super().__init__(detail=detail)


class UnauthenticatedPing(APIException):
    status_code = 403
    default_code = "unauthenticated_ping"

    def __init__(self, url):
        detail = "Unauthenticated ping of registered device. Use {}".format(url)
        super().__init__(detail=detail)


def get_external_ip_address(request):
    """Find the external IP address from the request"""
    # TODO: Handle IPv6 properly: http://www.steves-internet-guide.com/ipv6-guide/
    client_ip, is_routable = get_client_ip(request)
    if not is_routable and not settings.DEBUG:
        raise ExternalIPAddressNotRoutable(client_ip)
    if is_valid_ipv6(client_ip):
        raise ExternalIPAddressV6(client_ip)
    return client_ip


class SiteListView(LoginRequiredMixin, View):
    """List of a user's site"""

    def get(self, request, *args, **kwargs):
        context = {}
        if "message" in kwargs:
            context["message"] = kwargs["message"]
        context["sites"] = Site.objects.filter(owner=request.user)
        return render(request, "farms/site_list.html", context=context)


class SiteSetupView(LoginRequiredMixin, View):
    """Allows a user to create a site"""

    def get(self, request, *args, **kwargs):
        return render(request, "farms/site_setup.html", {"form": CreateSiteForm()})

    def post(self, request, *args, **kwargs):
        form = CreateSiteForm(request.POST)

        if form.is_valid():
            Site.objects.create(**form.cleaned_data, owner=request.user)
            return HttpResponseRedirect(reverse("site-list"))
        else:
            return render(request, "farms/site_setup.html", {"form": form}, status=400)


class APISiteDetailView(generics.RetrieveAPIView):
    """Details of one site"""

    permission_classes = (IsAuthenticated,)
    serializer_class = SiteSerializer
    queryset = Site.objects.all()


class APISiteListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SiteSerializer

    def get_queryset(self):
        user = self.request.user
        return Site.objects.filter(owner=user)


class CoordinatorSetupSelectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}

        client_ip, is_routable = get_client_ip(request)
        if not is_routable and not settings.DEBUG:
            context["error"] = (
                "Sorry, your external IP address can not be used for a lookup: %s"
                % client_ip
            )
            return render(
                request, "farms/coordinator_setup_select.html", context=context
            )

        coordinators = Coordinator.objects.filter(external_ip_address=client_ip)
        context["unregistered_coordinators"] = sorted(
            filter(lambda coordinator: not coordinator.site, coordinators),
            key=lambda coordinator: coordinator.modified_at,
        )
        context["registered_coordinators"] = sorted(
            filter(lambda coordinator: coordinator.site, coordinators),
            key=lambda coordinator: coordinator.modified_at,
        )
        return render(request, "farms/coordinator_setup_select.html", context=context)

    def post(self, request, *args, **kwargs):
        form = CoordinatorSetupSelectForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(
                reverse(
                    "coordinator-setup-register",
                    kwargs={"pk": form.cleaned_data["coordinator_id"]},
                ),
            )
        else:
            return render(
                request,
                "farms/coordinator_setup_select.html",
                {"form": form},
                status=400,
            )


class CoordinatorSetupRegisterView(LoginRequiredMixin, View):
    """The view to assign a coordinator to a site."""

    def get(self, request, *args, **kwargs):
        context = {}
        client_ip, is_routable = get_client_ip(request)
        if not is_routable and not settings.DEBUG:
            context["error"] = (
                "Sorry, your external IP address can not be used for a lookup: %s"
                % client_ip
            )
            return render(
                request, "farms/coordinator_setup_register.html", context=context
            )

        # Get all sites that do not have a coordinator
        sites = Site.objects.filter(coordinator__isnull=True).filter(owner=request.user)
        form = CoordinatorSetupRegistrationForm(sites=sites)
        return render(request, "farms/coordinator_setup_register.html", {"form": form},)

    def post(self, request, *args, **kwargs):
        sites = Site.objects.filter(coordinator__isnull=True).filter(owner=request.user)
        form = CoordinatorSetupRegistrationForm(request.POST, sites=sites)

        # Check if the request originates from a valid IP address
        client_ip, is_routable = get_client_ip(request)
        if not is_routable and not settings.DEBUG:
            form.add_error(
                None, "Your external IP address ({}) is not routable.".format(client_ip)
            )

        # Abort if the form is valid or any errors have been detected
        if not form.is_valid():
            return render(
                request, "farms/coordinator_setup_register.html", {"form": form},
            )

        # Abort if the request came from a different subnet
        coordinator = Coordinator.objects.get(id=kwargs["pk"])
        if client_ip != coordinator.external_ip_address:
            form.add_error(
                None,
                "Your external IP address ({}) does not match the coordinator's.".format(
                    client_ip
                ),
            )
            return render(
                request, "farms/coordinator_setup_register.html", {"form": form}
            )

        # Set the site and subdomain
        form.cleaned_data["site"].subdomain = (
            form.cleaned_data["subdomain_prefix"]
            + "."
            + settings.FARMS_SUBDOMAIN_NAMESPACE
            + "."
            + settings.SERVER_DOMAIN
        )
        form.cleaned_data["site"].save()
        coordinator.site = form.cleaned_data["site"]
        coordinator.save()
        # setup_subdomain_task.delay(coordinator.site.id)
        # TODO: Setup after registration
        # setup_subdomain_task.s(coordinator.site.id).apply()
        # messages.success(
        #     request, "Registration successful. Creating subdomain and credentials."
        # )
        return HttpResponseRedirect(reverse("site-list"))


class APICoordinatorPingView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        # Find the external IP address from the request
        # TODO: Handle IPv6 properly: http://www.steves-internet-guide.com/ipv6-guide/
        client_ip, is_routable = get_client_ip(request)
        if not is_routable and not settings.DEBUG:
            error_msg = "External IP address is not routable: %s" % client_ip
            return JsonResponse(data={"error": error_msg}, status=400)

        data = request.data.copy()
        data["external_ip_address"] = client_ip

        # Serialize the request
        serializer = CoordinatorPingSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        # If the coordinator has been registered, only allow authenticated view
        try:
            coordinator = Coordinator.objects.get(pk=serializer.validated_data["id"])
            if coordinator.site:
                url = CoordinatorSerializer(
                    coordinator, context={"request": request}
                ).data["url"]
                raise UnauthenticatedPing(url)
        except ObjectDoesNotExist:
            pass

        serializer.save()
        return JsonResponse(serializer.data, status=201)


class APICoordinatorListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = CoordinatorSerializer

    def get_queryset(self):
        return Coordinator.objects.filter(site__owner=self.request.user)


class APICoordinatorDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, pk):
        return JsonResponse(CoordinatorSerializer(Coordinator.objects.get(pk=pk)))


class APIMqttMessageListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = MqttMessageSerializer

    def get_queryset(self):
        coordinator = self.kwargs["coordinator"]
        return MqttMessage.objects.filter(coordinator=coordinator)


class APICoordinatorMqttView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        return


class APIControllerPingView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        # Extract the IP address and get the first matching coordinator
        external_ip_address = get_external_ip_address(request)

        # Return the local IP address of the coordinator or
        coordinator = Coordinator.objects.filter(
            external_ip_address=external_ip_address
        ).first()
        if coordinator:
            response = ControllerPingGetSerializer(
                {"coordinator_local_ip_address": coordinator.local_ip_address}
            )
        else:
            response = ControllerPingGetSerializer()

        return JsonResponse(response.data)

    def post(self, request):
        request_data = request.data.copy()
        request_data["external_ip_address"] = get_external_ip_address(request)

        # Serialize the request
        serializer = ControllerPingPostSerializer(data=request_data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        # If the controller has been registered, only allow authenticated view
        try:
            controller = Controller.objects.get(pk=serializer.validated_data["id"])
            if controller.coordinator:
                url = ControllerSerializer(
                    controller, context={"request": request}
                ).data["url"]
                raise UnauthenticatedPing(url)
        except ObjectDoesNotExist:
            pass

        serializer.save()
        return JsonResponse(serializer.data, status=201)


class APIControllerDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return JsonResponse(
            ControllerSerializer(Controller.objects.get(pk=request.user))
        )