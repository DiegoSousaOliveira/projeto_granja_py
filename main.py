import sdcard, network, time, json
from machine import Pin
from rpm import tachometer_handler, calculate_rpm
from firebase import send_rpm_to_firebase


# Configurações
WIFI_SSID = "EDNA"
WIFI_PASSWORD = "wwork197"

# Firebase
url = "https://rpm-bitdoglab-default-rtdb.firebaseio.com/rpm.json"

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


# Configuração SDCARD
sd = sdcard.SDCard(0, 18, 19, 16, 17, baudrate=0x10<<20, led=25, detect=15, wait=True)

# Pin do tacômetro
tachometerPin = Pin(3, Pin.IN, Pin.PULL_DOWN)

# Configurar interrupção
tachometerPin.irq(trigger=Pin.IRQ_RISING, handler=tachometer_handler)

# Conectar WiFi
if connect_wifi():
    try:
        while True:
            # Calcular RPM
            rpm, pulsos = calculate_rpm()
                
            # Enviar para Firebase a cada 5 leituras ou se RPM > 0
            if rpm > 0:
                # Enviar para Firebase
                sucesso = send_rpm_to_firebase(url, rpm, pulsos)
                
                with open("/sd/rpm.json", "a") as file:
                    file.write(
                        json.dumps({"rpm": rpm, "pulsos": pulsos, "timestamp": time.time()}) + "\n"
                    )
                
                        
            # Aguardar um pouco antes da próxima leitura
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário")

    except Exception as e:
        print(f"\n💥 Erro: {e}")
else:
    print("Conexão com a internet falhou!")

