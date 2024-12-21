import tkinter as tk
import paho.mqtt.client as mqtt
import time

# MQTT Configuration
BROKER = "localhost"
PORT = 1883

# Available parking slots (same as before)
parking_slots = {
    "electric": {"floor1": ["10", "11", "12"], "floor2": ["20", "21", "22"]},
    "motorcycle": {"floor1": ["13", "14"], "floor2": ["23", "24"]},
    "car": {"floor1": ["15", "16", "17", "18", "19"], "floor2": ["25", "26", "27", "28", "29"]},
}

occupied_slots = set()

def on_connect(client, userdata, flags, rc):
    """Handle successful connection to the MQTT broker."""
    if rc == 0:
        print(f"Connected to {BROKER} with result code {rc}")
        client.subscribe("parking/#")  # Subscribe to all parking topics
    else:
        print(f"Failed to connect with result code {rc}. Retrying...")
        time.sleep(5)  # Wait before retrying
        client.reconnect()

def on_disconnect(client, userdata, rc):
    """Handle disconnection and attempt reconnection."""
    print(f"Disconnected with result code {rc}. Reconnecting...")
    while rc != 0:
        try:
            client.reconnect()
            print("Reconnected successfully.")
            break
        except Exception as e:
            print(f"Reconnection failed: {e}. Retrying in 5 seconds.")
            time.sleep(5)  # Wait before retrying

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages and update slot status."""
    topic = msg.topic
    payload = msg.payload.decode()
    
    # Extract slot number from topic
    slot = topic.split("/")[-1][4:]
    floor = topic.split("/")[-2]

    if payload == "occupied":
        occupied_slots.add(slot)
    elif payload == "free":
        occupied_slots.remove(slot)

    update_slots_display()

def update_slots_display():
    """Update the display of available and occupied slots in the Tkinter GUI."""
    # Clear previous content in the frames
    for widget in electric_frame.winfo_children():
        widget.destroy()
    for widget in car_frame.winfo_children():
        widget.destroy()
    for widget in motorcycle_frame.winfo_children():
        widget.destroy()

    # Electric column
    tk.Label(electric_frame, text="Electric", font=("Arial", 12, "bold")).pack(anchor="w")
    for floor, slots in parking_slots["electric"].items():
        tk.Label(electric_frame, text=f"{floor.capitalize()}:", font=("Arial", 10, "italic")).pack(anchor="w")
        for slot in slots:
            status = "Occupied" if slot in occupied_slots else "Available"
            color = "red" if status == "Occupied" else "green"
            tk.Label(electric_frame, text=f"Slot {slot}: {status}", fg=color).pack(anchor="w")

    # Car column
    tk.Label(car_frame, text="Car", font=("Arial", 12, "bold")).pack(anchor="w")
    for floor, slots in parking_slots["car"].items():
        tk.Label(car_frame, text=f"{floor.capitalize()}:", font=("Arial", 10, "italic")).pack(anchor="w")
        for slot in slots:
            status = "Occupied" if slot in occupied_slots else "Available"
            color = "red" if status == "Occupied" else "green"
            tk.Label(car_frame, text=f"Slot {slot}: {status}", fg=color).pack(anchor="w")

    # Motorcycle column
    tk.Label(motorcycle_frame, text="Motorcycle", font=("Arial", 12, "bold")).pack(anchor="w")
    for floor, slots in parking_slots["motorcycle"].items():
        tk.Label(motorcycle_frame, text=f"{floor.capitalize()}:", font=("Arial", 10, "italic")).pack(anchor="w")
        for slot in slots:
            status = "Occupied" if slot in occupied_slots else "Available"
            color = "red" if status == "Occupied" else "green"
            tk.Label(motorcycle_frame, text=f"Slot {slot}: {status}", fg=color).pack(anchor="w")

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message

# Set up the GUI
root = tk.Tk()
root.title("Parking Status Display")
root.geometry("500x350")

# Create Frames to organize layout
status_frame = tk.Frame(root)
status_frame.pack(pady=20)

electric_frame = tk.Frame(status_frame, width=150)
electric_frame.pack(side="left", fill="both", expand=True, padx=20)

car_frame = tk.Frame(status_frame, width=150)
car_frame.pack(side="left", fill="both", expand=True, padx=20)

motorcycle_frame = tk.Frame(status_frame, width=150)
motorcycle_frame.pack(side="left", fill="both", expand=True, padx=20)

# Run the MQTT client loop in the background
try:
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"Failed to connect to broker: {e}. Please check your connection.")

# Run the Tkinter event loop
root.mainloop()
