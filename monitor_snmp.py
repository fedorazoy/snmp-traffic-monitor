import sys
import time
from pysnmp.hlapi import *
import argparse

def snmp_get(community, ip, oid):
    """Consulta SNMP e retorna o valor associado a um OID"""
    error_indication, error_status, error_index, var_binds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if error_indication or error_status:
        print(f"Erro SNMP: {error_indication or error_status}")
        sys.exit(1)

    for var_bind in var_binds:
        return var_bind[1]


def monitor_traffic(community, ip, interface_id, interval=30):
    """Monitora o tráfego de rede e calcula taxas de upload e download"""
    # OIDs para ifOutOctets e ifInOctets (trafego de saída e entrada)
    oid_out = f'1.3.6.1.2.1.2.2.1.16.{interface_id}'  # Trafego de saída
    oid_in = f'1.3.6.1.2.1.2.2.1.10.{interface_id}'  # Trafego de entrada

    # Coleta os dados iniciais
    out1 = snmp_get(community, ip, oid_out)
    in1 = snmp_get(community, ip, oid_in)


    time.sleep(interval)

    # Coleta os dados após o intervalo
    out2 = snmp_get(community, ip, oid_out)
    in2 = snmp_get(community, ip, oid_in)

    # Calculando a diferença (bytes)
    out_diff = out2 - out1
    in_diff = in2 - in1

    # Convertendo para bits
    upload_bps = (out_diff * 8) / interval
    download_bps = (in_diff * 8) / interval

    # Convertendo para Kilobits
    upload_kbps = upload_bps / 1024
    download_kbps = download_bps / 1024


    print(f'Taxa de Upload: {upload_kbps:.2f} Kbps')
    print(f'Taxa de Download: {download_kbps:.2f} Kbps')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Monitoramento de tráfego de rede via SNMP.")
    parser.add_argument('community', help="Comunidade SNMP (ex: public)")
    parser.add_argument('ip', help="Endereço IP do dispositivo (ex: 192.168.1.1)")
    parser.add_argument('interface', type=int, help="ID da interface (ex: 1 para eth0)")
    parser.add_argument('--interval', type=int, default=30,
                        help="Intervalo de tempo em segundos entre as medições (padrão 30s)")

    args = parser.parse_args()


    monitor_traffic(args.community, args.ip, args.interface, args.interval)