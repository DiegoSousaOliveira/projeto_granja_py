import urequests
from time import time
import json

def check_firebase_rules(url):
    """Verifica se as regras do Firebase permitem escrita"""
    
    try:
        response = urequests.get(url)
        status = response.status_code
        response.close()
        
        return status == 200
            
    except Exception as e:
        print("Erro regras: ", e)
        return False


def send_rpm_to_firebase(url, rpm_value, pulsos):
    """Envia dados de RPM para Firebase"""
    
    # Dados completos
    dados = {
        "rpm": float(rpm_value),
        "pulsos": pulsos,
        "timestamp": time()
    }
    
    try:
        response = urequests.post(url, data=json.dumps(dados))
        status =  response.status_code
        response.close()
        
        
        return status == 200
            
    except Exception as e:
        print("Erro envio: ", e)
        return False
    

