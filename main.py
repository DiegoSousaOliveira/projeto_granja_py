from machine import Pin
import network
import time
import json
import urequests

# Configurações
WIFI_SSID = "Labirang"
WIFI_PASSWORD = "1fp1*007"

# Variável global para contagem RPM
rpm_counter = 0

# Pin do tacômetro
tachometerPin = Pin(16, Pin.IN, Pin.PULL_DOWN)

# Tempo de amostragem (segundos)
SAMPLING_TIME = 1

def tachometer_handler(pin):
    """Handler da interrupção para contar pulsos"""
    global rpm_counter
    rpm_counter += 1

def connect_wifi():
    """Conecta ao WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        for i in range(30):
            if wlan.isconnected():
                break
            time.sleep(0.5)
            print(".", end="")
    
    if wlan.isconnected():
        return True
    
    return False

def check_firebase_rules():
    """Verifica se as regras do Firebase permitem escrita"""
    
    test_url = "https://rpm-bitdoglab-default-rtdb.firebaseio.com/.json"
    
    try:
        response = urequests.get(test_url)
        
        if response.status_code == 200:
            return True
        else:
            return False
            
    except Exception as e:
        return False

def send_rpm_to_firebase(rpm_value, pulsos):
    """Envia dados de RPM para Firebase"""
    
    # URL CORRETA com .json
    url = "https://rpm-bitdoglab-default-rtdb.firebaseio.com/rpm.json"
    
    # Dados completos
    dados = {
        "rpm": float(rpm_value),
        "pulsos": pulsos,
        "timestamp": time.time()
    }
    
    try:
        response = urequests.post(url, data=json.dumps(dados))
        response.close()
        
        
        if response.status_code == 200:
            return True
        else:
            return False
            
    except Exception as e:
        return False

def calculate_rpm():
    """Calcula RPM baseado na contagem de pulsos"""
    global rpm_counter
    
    # Esperar tempo de amostragem
    time.sleep(SAMPLING_TIME)
    
    # Calcular RPM
    # 2 pulsos por volta (2 faixas brancas no rotor)
    revolutions_per_sampling_time = rpm_counter / 2
    revolutions_per_sec = revolutions_per_sampling_time / SAMPLING_TIME
    revolutions_per_minute = revolutions_per_sec * 60
    
    # Resetar contador para próxima amostra
    current_counter = rpm_counter
    rpm_counter = 0
    
    return revolutions_per_minute, current_counter

def main():
    # Configurar interrupção
    tachometerPin.irq(trigger=Pin.IRQ_RISING, handler=tachometer_handler)
    
    # Conectar WiFi
    if not connect_wifi():
        return
    
    try:
        while True:
            # Calcular RPM
            rpm, pulsos = calculate_rpm()
            
            # Enviar para Firebase a cada 5 leituras ou se RPM > 0
            if rpm > 0:
                # Enviar para Firebase
                sucesso = send_rpm_to_firebase(rpm, pulsos)
                    
            # Aguardar um pouco antes da próxima leitura
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário")

    except Exception as e:
        print(f"\n💥 Erro: {e}")
            

main()

