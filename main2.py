from machine import Pin
import network
import time
import json
import urequests

# Configurações
WIFI_SSID = "POCO X5"
WIFI_PASSWORD = "shayder9080"

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
    print("\n📡 Iniciando conexão WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Conectando em: {WIFI_SSID}")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        for i in range(30):
            if wlan.isconnected():
                break
            time.sleep(0.5)
            print(".", end="")
    
    if wlan.isconnected():
        print(f"\n✅ WiFi conectado! IP: {wlan.ifconfig()[0]}")
        return True
    
    print("\n❌ Falha ao conectar WiFi")
    return False

def check_connection():
    """Verifica se consegue conectar à internet"""
    
    print(f"\n🔍 Testando conexão de rede...")
    
    try:
        print("Tentando HTTP em google.com...")
        response = urequests.get("http://google.com", timeout=5)
        print(f"✅ Conexão funcionando! Status: {response.status_code}")
        response.close()
        return True
    except Exception as e:
        print(f"⚠️ Erro na conexão: {e}")
        return False

def send_rpm_to_firebase(rpm_value, pulsos):
    """Envia dados de RPM para Firebase"""
    
    url = "https://rpm-bitdoglab-default-rtdb.firebaseio.com/rpm.json"
    
    dados = {
        "rpm": float(rpm_value),
        "pulsos": pulsos,
        "timestamp": time.time()
    }
    
    json_string = json.dumps(dados)
    
    try:
        print(f"\n📤 Enviando para Firebase: RPM={rpm_value:.2f}, Pulsos={pulsos}")
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = urequests.post(url, data=json_string, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Enviado com sucesso!")
            response.close()
            return True
        else:
            resp_text = response.text
            print(f"Resposta: {resp_text}")
            response.close()
            print(f"⚠️ Erro na resposta: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Erro ao enviar: {type(e).__name__}: {e}")
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
    
    print(f"📊 Pulsos detectados: {rpm_counter} | Revoluções: {revolutions_per_sampling_time} | RPM calculado: {revolutions_per_minute:.2f}")
    
    # Resetar contador para próxima amostra
    current_counter = rpm_counter
    rpm_counter = 0
    
    return revolutions_per_minute, current_counter

def main():
    print("\n🚀 Iniciando programa de monitoramento de RPM...")
    print(f"Pino do tacômetro: GPIO16")
    print(f"Tempo de amostragem: {SAMPLING_TIME}s")
    
    # Configurar interrupção
    tachometerPin.irq(trigger=Pin.IRQ_RISING, handler=tachometer_handler)
    print("✅ Interrupção do tacômetro configurada")
    
    # Conectar WiFi
    wlan = network.WLAN(network.STA_IF)
    if not connect_wifi():
        print("❌ Não foi possível conectar ao WiFi. Saindo...")
        return
    
    # Testar conexão com internet
    time.sleep(1)
    check_connection()
    
    try:
        print("\n▶️  Iniciando loop principal...")
        while True:
            # Calcular RPM
            rpm, pulsos = calculate_rpm()
            
            # Verificar conexão WiFi
            if wlan.isconnected():
                print(f"📶 WiFi OK: {wlan.ifconfig()[0]}")
            else:
                print("⚠️ WiFi desconectado! Tentando reconectar...")
                if not connect_wifi():
                    print("❌ Falha ao reconectar")
                    continue
            
            # Enviar para Firebase se RPM > 0
            if rpm > 0:
                sucesso = send_rpm_to_firebase(rpm, pulsos)
                if sucesso:
                    print("✅ Dados salvos!")
                else:
                    print("⚠️ Falha ao enviar")
                    
            # Aguardar antes da próxima leitura
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário")

    except Exception as e:
        print(f"\n💥 Erro: {type(e).__name__}: {e}")

main()

