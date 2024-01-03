import asyncio
import websockets
import paramiko
import threading
import time

async def ssh_connect(ssh_details, output_queue, input_queue, close_event):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_details['host'], username=ssh_details['username'], password=ssh_details['password'])
    print("SSH-Verbindung erfolgreich aufgebaut.")

    term_width_chars = ssh_details['cols']
    term_height_chars = ssh_details['rows']

    ssh_shell = ssh.invoke_shell(term='vt100', width=term_width_chars, height=term_height_chars)

    def read_ssh_output():
        while not close_event.is_set():
            if ssh_shell.recv_ready():
                data = ssh_shell.recv(1024).decode('utf-8')
                asyncio.run(output_queue.put(data))
            else:
                time.sleep(0.1)

    read_thread = threading.Thread(target=read_ssh_output)
    read_thread.start()

    while not close_event.is_set():
        if not input_queue.empty():
            command = input_queue.get_nowait()
            ssh_shell.send(command)
        await asyncio.sleep(0.01)

    ssh.close()
    print("SSH-Verbindung geschlossen.")

async def websocket_server(websocket, path):
    print("WebSocket-Server gestartet.")
    ssh_details = {
        'host': None,
        'username': 'WuDu',
        'password': 'passwort',
        'cols': None,  # Initialwert auf None gesetzt
        'rows': None,  # Initialwert auf None gesetzt
    }
    output_queue = asyncio.Queue()
    input_queue = asyncio.Queue()
    close_event = threading.Event()

    ssh_thread = None
    ssh_connected = False  # Statusvariable hinzufügen, die angibt, ob die SSH-Verbindung bereits hergestellt wurde

    async def receive_messages():
        nonlocal ssh_thread, ssh_connected
        try:
            while not close_event.is_set():
                message = await asyncio.wait_for(websocket.recv(), timeout=600)

                # Wenn SSH verbunden ist, fügen Sie alle Nachrichten zur input_queue hinzu
                if ssh_connected:
                    input_queue.put_nowait(message)
                else:
                    if message.startswith('SSH_IP:'):
                        ssh_details['host'] = message[len('SSH_IP:'):]
                    elif message.startswith('TERM_SIZE:'):
                        size = message[len('TERM_SIZE:'):].split(',')
                        ssh_details['cols'], ssh_details['rows'] = int(size[0]), int(size[1])

                    if ssh_details['host'] and ssh_details['cols'] and ssh_details['rows'] and ssh_thread is None:
                        ssh_thread = threading.Thread(target=lambda: asyncio.run(ssh_connect(ssh_details, output_queue, input_queue, close_event)))
                        ssh_thread.start()
                        ssh_connected = True  # Setzen Sie ssh_connected auf True, wenn die SSH-Verbindung gestartet wird

                await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            print("Keine Aktivität für 10 Minuten, schließe die Verbindung.")
            close_event.set()
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket-Verbindung vorzeitig geschlossen.")
            close_event.set()

    async def send_messages():
        while not close_event.is_set():
            try:
                response = await output_queue.get()
                await websocket.send(response)
            except:
                await websocket.send(' ')
                await asyncio.sleep(0.1)

    await asyncio.gather(receive_messages(), send_messages())

start_server = websockets.serve(
    websocket_server,
    "localhost", 8765
)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
