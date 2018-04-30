from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from . import sensors
from .forms import EditInfluxDBForm, NewInfluxDBForm
from ..models import InfluxDB
from .. import influx_db_client


@sensors.route('/influx_db')
@login_required
def index():
    """List Influx databases"""
    return render_template('sensors/index.html', influx_dbs=current_user.influx_dbs)


@sensors.route('/influx_db/<int:influx_db_id>', methods=['GET', 'POST'])
@login_required
def edit_influx_db(influx_db_id):
    """Modify Influx databases"""
    influx_db = InfluxDB.query.get(influx_db_id)
    form = EditInfluxDBForm()
    if form.validate_on_submit():
        # Check which button was pressed
        if form.reset.data:
            influx_db.reset_database(influx_db_client)
            flash('Database <em>{}</em> successfully reset'.format(influx_db.name),
                  'form-success')
        if form.delete.data:
            influx_db.drop_database(influx_db_client)
            flash('Database <em>{}</em> was successfully deleted'.format(influx_db.name),
                  'form-success')
            return redirect(url_for('sensors.index'))
    return render_template('sensors/index.html',
                           form=form,
                           influx_db=influx_db,
                           view='edit')


@sensors.route('/influx_db/new_database', methods=['GET', 'POST'])
@login_required
def new_influx_db():
    """Create a new InlfluxDB"""
    form = NewInfluxDBForm()
    if form.validate_on_submit():
        influx_db = InfluxDB(name=form.name.data, owner_id=current_user.id)
        influx_db.create_database(influx_db_client)
        flash('Database <em>{}</em> successfully created'.format(influx_db.name),
              'form-success')
        return redirect(url_for('sensors.index'))
    return render_template('sensors/index.html', form=form, view='new')