# Variável global para contagem RPM
rpm_counter = 0

# Tempo de amostragem (segundos)
SAMPLING_TIME = 1

def tachometer_handler(pin):
    """Handler da interrupção para contar pulsos"""
    global rpm_counter
    rpm_counter += 1

def calculate_rpm():
    """Calcula RPM baseado na contagem de pulsos"""
    global SAMPLING_TIME, rpm_counter
    
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
