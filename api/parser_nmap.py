import xmltodict


def parse_nmap_xml(caminho_xml):
    with open(caminho_xml, "r", encoding="utf-8") as f:
        data = xmltodict.parse(f.read())

    hosts = data["nmaprun"].get("host", [])
    if type(hosts) is dict:
        hosts = [hosts]

    resultados = []

    for host in hosts:
        ports = host.get("ports", {}).get("port", [])
        if type(ports) is dict:
            ports = [ports]

        for p in ports:
            porta = int(p["@portid"])
            protocolo = p["@protocol"]
            servico = p.get("service", {}).get("@name", "unknown")
            # service = p.get("service", {})
            # servico = service.get("@name", "unknown")
            estado = p.get("state", {}).get("@state", "unknown")

            resultados.append(
                {
                    "porta": porta,
                    "protocolo": protocolo,
                    "servico": servico,
                    "estado": estado,
                }
            )

    return resultados


if __name__ == "__main__":
    dados = parse_nmap_xml("/data/exemplos_xml/scan.xml")
    print(dados)
