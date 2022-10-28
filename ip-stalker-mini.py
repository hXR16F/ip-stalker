from requests import get
from webbrowser import open
from re import findall, search
import dearpygui.dearpygui as dpg
from subprocess import check_output, CalledProcessError


# TODO: add status label to check if there is pending operation or not

def main():
    dpg.create_context()
    dpg.create_viewport(title="IP Stalker Mini", width=333, height=500)
    dpg.setup_dearpygui()

    global item_index
    item_index = 0

    def toggle_buttons(func):
        def inner(*args, **kwargs):
            for tag in ["button_recon", "button_ping", "button_lookup"]:
                dpg.configure_item(tag, enabled=False)

            returned_value = func(*args, **kwargs)

            for tag in ["button_recon", "button_ping", "button_lookup"]:
                dpg.configure_item(tag, enabled=True)

            return returned_value

        return inner

    def clear():
        global item_index
        for x in range(item_index):
            if dpg.does_alias_exist(f"item_{x}"):
                dpg.delete_item(f"item_{x}")

    def filter_ip(ip):
        if not ip:
            return False
        else:
            if "/" in ip:
                return False

        return True

    @toggle_buttons
    def my_ip():
        my_ip = get("https://api.ipify.org/").content.decode()
        dpg.set_value(ip, value=my_ip)

    @toggle_buttons
    def recon():
        global item_index
        ip = dpg.get_value("ip")
        if not filter_ip(ip):
            return

        pattern = "\d+.\d+.\d+.\d+"
        if not search(pattern, ip):
            ip = lookup(True)
            if ip == None:
                return

        result = get(f"https://api.iplocation.net/?ip={ip}").json()
        country_name = result["country_name"]
        country_code = result["country_code2"]
        isp = result["isp"]

        dpg.add_text(
            f"IP Address : {ip}\n   Country : {country_name} ({country_code})\n       ISP : {isp}", parent="Primary Window", tag=f"item_{item_index}")
        item_index += 1

    @toggle_buttons
    def ping():
        global item_index
        ip = dpg.get_value("ip")
        if not filter_ip(ip):
            return

        try:
            result = check_output(["ping", "-n", "1", "-w", "3", ip]).decode()
        except CalledProcessError:
            dpg.add_text(f"Host '{ip}' is not responding.",
                         parent="Primary Window", tag=f"item_{item_index}")
        else:
            pattern = "time.\d+ms"
            latency_list = []
            for item in findall(pattern, result):
                latency_list.append(int(item[5:-2]))

            average_latency = sum(latency_list) / len(latency_list)
            dpg.add_text(f"Host '{ip}' is up ({average_latency} ms).",
                         parent="Primary Window", tag=f"item_{item_index}")
        finally:
            item_index += 1

    @toggle_buttons
    def lookup(*args):
        global item_index
        ip = dpg.get_value("ip")
        if not filter_ip(ip):
            return

        if args == ():
            silent = False
        else:
            for arg in args:
                if arg == True:
                    silent = True
                else:
                    silent = False

        pattern = "\d+.\d+.\d+.\d+"
        ip_list = []
        try:
            ip_list = findall(pattern, ip)[0].split(".")
        except:
            is_ip = False
            pass

        correct = 0
        for segment in ip_list:
            try:
                if int(segment) >= 0 and int(segment) <= 255:
                    pass
                    correct += 1
                else:
                    is_ip = False
                    break
            except:
                is_ip = False
                break

        if correct == 4:
            is_ip = True

        if is_ip:
            pattern = "Name:    .+"
            try:
                result = check_output(["nslookup", ip]).decode()
                hostname = findall(pattern, result)[0].strip()[9::]
            except:
                if not "Name:" in result:
                    if silent == False:
                        dpg.add_text(f"'{ip}' has a non-existent domain.",
                                     parent="Primary Window", tag=f"item_{item_index}")
                        item_index += 1

                    return f"'{ip}' has a non-existent domain."
            else:
                if silent == False:
                    dpg.add_text(f"IP Address : {ip}\n  Hostname : {hostname}",
                                 parent="Primary Window", tag=f"item_{item_index}")
                    item_index += 1

                return hostname
        else:
            hostname = ip
            pattern = "\d+.\d+.\d+.\d+"
            try:
                result = check_output(["ping", "-n", "1", ip]).decode()
                ip_address = findall(pattern, result)[0]
            except:
                pass
            else:
                if silent == False:
                    dpg.add_text(f"IP Address : {ip_address}\n  Hostname : {hostname}",
                                 parent="Primary Window", tag=f"item_{item_index}")
                    item_index += 1

                return ip_address

    def port_scan():
        open("https://hackertarget.com/nmap-online-port-scanner/")

    def rdap():
        ip = dpg.get_value("ip")
        if not filter_ip(ip):
            return

        pattern = "\d+.\d+.\d+.\d+"
        try:
            findall(pattern, ip)[0].split(".")
        except:
            ip = lookup(True)
        finally:
            open(f"https://rdap.db.ripe.net/ip/{ip}")

    with dpg.window(tag="Primary Window"):
        with dpg.group(horizontal=True):
            dpg.add_text("IP Stalker Mini")

        with dpg.group(horizontal=True):
            dpg.add_button(label="My IP", callback=my_ip)
            ip = dpg.add_input_text(
                hint="type IP address here", width=250, no_spaces=True, tag="ip")

        with dpg.group(horizontal=True):
            dpg.add_text("Internal")
            dpg.add_button(label="Recon", callback=recon, tag="button_recon")
            dpg.add_button(label="Ping", callback=ping, tag="button_ping")
            dpg.add_button(label="Lookup", callback=lookup,
                           tag="button_lookup")

        with dpg.group(horizontal=True):
            dpg.add_text("External")
            dpg.add_button(label="Port scan", callback=port_scan)
            dpg.add_button(label="RDAP", callback=rdap)
            dpg.add_button(label="Clear", callback=clear, indent=258)

    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
    