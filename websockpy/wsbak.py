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
    ssh_shell = ssh.invoke_shell()

    def read_ssh_output():
        while not close_event.is_set():
            if ssh_shell.recv_ready():
                data = ssh_shell.recv(1024).decode('utf-8')
                asyncio.run(output_queue.put(data))
            else:
                time.sleep(0.1)  # Kleine Pause, um CPU-Überlastung zu vermeiden

    read_thread = threading.Thread(target=read_ssh_output)
    read_thread.start()

    while not close_event.is_set():
        if not input_queue.empty():
            command = input_queue.get_nowait()
            ssh_shell.send(command)
        await asyncio.sleep(0.01)  # Nicht-blockierender Sleep

    ssh.close()
    print("SSH-Verbindung geschlossen.")

async def websocket_server(websocket, path):
    print("WebSocket-Server gestartet.")
    ssh_details = {
        'host': None,
        'username': 'WuDu',
        'password': 'passwort',
        'close_connection': False
    }
    output_queue = asyncio.Queue()
    input_queue = asyncio.Queue()
    close_event = threading.Event()

    ssh_thread = None

    async def receive_messages():
        nonlocal ssh_thread
        try:
            while not close_event.is_set():
                message = await asyncio.wait_for(websocket.recv(), timeout=600)  # 10 Minuten Timeout
                if message.startswith('SSH_IP:'):
                    ssh_details['host'] = message[len('SSH_IP:'):]
                    if ssh_thread is None:
                        ssh_thread = threading.Thread(target=lambda: asyncio.run(ssh_connect(ssh_details, output_queue, input_queue, close_event)))
                        ssh_thread.start()
                else:
                    input_queue.put_nowait(message)
                await asyncio.sleep(0.1)  # Nicht-blockierender Sleep
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
                await asyncio.sleep(0.1)  # Nicht-blockierender Sleep


    await asyncio.gather(receive_messages(), send_messages())

start_server = websockets.serve(
    websocket_server,
    "localhost", 8765
)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
