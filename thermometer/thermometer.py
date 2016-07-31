# Thermometer API based on Flask.
# Wery similar to the camera API.
# Temperatures are measured using a w1 sensor
import os
import time
import uuid
from glob import glob
from flask import Flask, url_for, jsonify, send_file

import temperature # For actual temperature measurements

thermometers = {}
app = Flask(__name__)


# custom exceptions
class InvalidThermometer(ValueError):
    pass

class InvalidTemperature(ValueError):
    pass


# custom error handlers
@app.errorhandler(InvalidThermometer)
def invalid_thermometer(e):
    return jsonify({'error': 'thermometer not found'}), 404

@app.errorhandler(InvalidTemperature)
def invalid_temperature(e):
    return jsonify({'error': 'temperature not found'}), 404

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'resource not found'}), 404

@app.errorhandler(405)
def method_not_supported(e):
    return jsonify({'error': 'method not supported'}), 405

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'internal server error'}), 500

# helper functions
def get_thermometer_from_id(thermid):
    """Return the thermometer object for the given thermometer ID."""
    thermometer = thermometers.get(thermid)
    if thermometer is None:
        raise InvalidThermometer()
    return thermometer


# Thermometer class
class Thermometer(object):
    """Thermometer handler class."""
    def __init__(self):
        self.thermid = 'w1'

    def get_url(self):
        return url_for('get_thermometer', thermid=self.thermid, _external=True)

    def export_data(self):
        return {'self_url': self.get_url(),
                'temperatures_url': self.get_temperatures_url(),
                'emulated': self.is_emulated()}

    def get_temperatures_url(self):
        return url_for('get_thermometer_temperatures', thermid=self.thermid, _external=True)

    def get_temperatures(self):
        return [os.path.basename(f) for f in glob(self.thermid + '/*.txt')]

    def get_temperature_path(self, filename):
        path = self.thermid + '/' + filename
        if not os.path.exists(path):
            raise InvalidTemperature()
        return path

    def get_temperature(self, filename):
        resp = 'error'
        with open(filename) as f:
            resp = f.read()
        return {'temperature': str(resp)}

    def get_new_temperature_filename(self):
        return uuid.uuid4().hex + '.txt'

    def is_emulated(self):
        return False

    def capture(self):
        """Capture a temperature."""
        filename = self.thermid + '/' + self.get_new_temperature_filename()
        resp = temperature.measure_temp()
        with open(filename, 'w') as f:
            f.write(str(resp))
        return filename


thermometers['w1'] = Thermometer()

@app.route('/thermometers/', methods=['GET'])
def get_thermometers():
    """Return a list of available thermometers."""
    return jsonify({'thermometer': [url_for('get_thermometer', thermid=thermid,
                                        _external=True)
                                for thermid in thermometers.keys()]})

@app.route('/thermometers/<thermid>', methods=['GET'])
def get_thermometer(thermid):
    """Return information about a thermometer."""
    thermometer = get_thermometer_from_id(thermid)
    return jsonify(thermometer.export_data())

@app.route('/thermometers/<thermid>/temperatures/', methods=['GET'])
def get_thermometer_temperatures(thermid):
    """Return the collection of temperatures of a thermometer."""
    thermometer = get_thermometer_from_id(thermid)
    temperatures = thermometer.get_temperatures()
    return jsonify({'temperatures': [url_for('get_temperature', thermid=thermid,
                                     filename=temperature, _external=True)
                                     for temperature in temperatures]})

@app.route('/thermometers/<thermid>/temperatures/<filename>', methods=['GET'])
def get_temperature(thermid, filename):
    """Return a temperature."""
    thermometer = get_thermometer_from_id(thermid)
    path = thermometer.get_temperature_path(filename)
    return jsonify(thermometer.get_temperature(path))

@app.route('/thermometers/<thermid>/temperatures/', methods=['POST'])
def capture_temperature(thermid):
    """Capture a temperature and store it on disk."""
    thermometer = get_thermometer_from_id(thermid)
    filename = thermometer.capture()
    return jsonify({}), 201, {'Location': url_for('get_temperature', thermid=thermid,
                                                  filename=filename,
                                                  _external=True)}

@app.route('/thermometers/<thermid>/temperatures/<filename>', methods=['DELETE'])
def delete_temperature(thermid, filename):
    """Delete a temperature."""
    thermometer = get_thermometer_from_id(thermid)
    path = thermometer.get_temperature_path(filename)
    os.remove(path)
    return jsonify({})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
