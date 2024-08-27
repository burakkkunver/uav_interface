from pymavlink import mavutil
import time
from PyQt5.QtCore import QThread, pyqtSignal

class DroneData(QThread):
    data_updated = pyqtSignal(str, bool, str, str, bool, str, str, bool, str)

    def __init__(self):
        super().__init__()
        self.feniks_active = False
        self.alaca_active = False
        self.korfez_active = False

    def run(self):
        while True:
            self.feniks_data()
            # self.alaca_data()  # Şimdilik devre dışı bırakıldı
            # self.korfez_data() # Şimdilik devre dışı bırakıldı
            time.sleep(1)  # Verileri 1 saniyede bir güncelle

    def feniks_data(self):
        try:
            # Feniks bağlantı bilgilerini buraya girin
            feniks_vehicle = mavutil.mavlink_connection('udp:127.0.0.1:14550') 
            feniks_vehicle.wait_heartbeat()
            self.feniks_active = True

            # Feniks verilerini çekme
            battery = feniks_vehicle.recv_match(type='BATTERY_STATUS', blocking=True)
            feniks_battery = f"Pil Yüzdesi: {battery.battery_remaining}\n"

            message = feniks_vehicle.recv_match(type='VFR_HUD', blocking=True)
            feniks_airspeed = f"Hız: {message.airspeed}\n"

            attitude = feniks_vehicle.recv_match(type='ATTITUDE', blocking=True)
            feniks_attitude = f"Yaw: {attitude.yaw}, Pitch: {attitude.pitch}, Roll: {attitude.roll}\n"

            gps_raw_int = feniks_vehicle.recv_match(type='GPS_RAW_INT', blocking=True)
            feniks_gps = f"GPS Fix Type: {gps_raw_int.fix_type}, Latitude: {gps_raw_int.lat}, Longitude: {gps_raw_int.lon}\n"

            global_position_int = feniks_vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
            feniks_altitude = f"Relative Altitude: {global_position_int.relative_alt}\n"

            heartbeat = feniks_vehicle.recv_match(type='HEARTBEAT', blocking=True)
            feniks_heartbeat = f"Vehicle Type: {heartbeat.type}, Autopilot: {heartbeat.autopilot}\n"

            sys_status = feniks_vehicle.recv_match(type='SYS_STATUS', blocking=True)
            feniks_sys_status = f"System Voltage: {sys_status.voltage_battery} mV\n"

            rc_channels = feniks_vehicle.recv_match(type='RC_CHANNELS', blocking=True)
            feniks_rc_channels = f"RC Channel 1: {rc_channels.chan1_raw}, RC Channel 2: {rc_channels.chan2_raw}\n"

            raw_imu = feniks_vehicle.recv_match(type='RAW_IMU', blocking=True)
            feniks_raw_imu = f"Accel X: {raw_imu.xacc}, Accel Y: {raw_imu.yacc}, Accel Z: {raw_imu.zacc}\n"

            power_status = feniks_vehicle.recv_match(type='POWER_STATUS', blocking=True)
            feniks_power_status = f"Voltage 5V: {power_status.Vcc}, Flags: {power_status.flags}\n"

            msg = feniks_vehicle.recv_match(type='HEARTBEAT', blocking=True)
            feniks_mode = f"Mode: {mavutil.mode_string_v10(msg)}\n"

            # Tüm verileri birleştir
            feniks_all_data = f"""
            {feniks_battery}
            {feniks_airspeed}
            {feniks_attitude}
            {feniks_gps}
            {feniks_altitude}
            {feniks_heartbeat}
            {feniks_sys_status}
            {feniks_rc_channels}
            {feniks_raw_imu}
            {feniks_power_status}
            {feniks_mode}
            """

            self.data_updated.emit(
                "Feniks", self.feniks_active, feniks_all_data,
                "Alaca", self.alaca_active, "Alaca Verileri",
                "Korfez", self.korfez_active, "Korfez Verileri"
            )
        except Exception as e:
            self.feniks_active = False
            print(f"Feniks bağlantı hatası: {e}")
            self.data_updated.emit(
                "Feniks", self.feniks_active, "Feniks Bağlantı Hatası",
                "Alaca", self.alaca_active, "Alaca Verileri",
                "Korfez", self.korfez_active, "Korfez Verileri"
            )

    # def alaca_data(self):
    #     # ... Alaca ile ilgili kodlar burada olabilir ...
    #     pass  # Şimdilik boş

    # def korfez_data(self):
    #     # ... Korfez ile ilgili kodlar burada olabilir ...
    #     pass  # Şimdilik boş