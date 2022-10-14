
def getNORD():
    import os
    proxylist=[]
    for vpn in os.listdir('/root/Downloads/nordvpn/'):
        if '.txt' in vpn:
            continue
        with open(f'/root/Downloads/nordvpn/{vpn}', "r") as text_file:
            text_file.seek(0)
            apilist = text_file.read().split('\n')
            text_file.close()

        proxy = [f"{apilist[3].split(' ')[1]}:80",'HTTP']
        proxylist.append(proxy)
        print(f'Added {vpn}!')

    return proxylist