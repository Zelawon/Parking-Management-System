import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt

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

# Callback for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully.")
    else:
        print(f"Failed to connect with result code {rc}")
        messagebox.showerror("MQTT Error", f"Failed to connect to MQTT broker. Error code: {rc}")

# Callback for when the client disconnects from the broker
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection. Reconnecting...")
        client.reconnect()  # Try to reconnect
        messagebox.showwarning("MQTT Warning", "Disconnected from MQTT broker, attempting to reconnect...")

# Callback for logging messages
def on_log(client, userdata, level, buf):
    print(f"MQTT log: {buf}")

# Callback for message publishing result
def on_publish(client, userdata, mid):
    print(f"Message published successfully. Message ID: {mid}")

# Callback for message publishing failure
def on_publish_fail(client, userdata, mid):
    print(f"Failed to publish message. Message ID: {mid}")
    messagebox.showerror("MQTT Publish Error", f"Failed to publish message with ID: {mid}")

def find_free_slot(vehicle_type):
    """Finds the first free slot for the selected vehicle type on the first available floor."""
    for floor, slots in parking_slots[vehicle_type].items():
        for slot in slots:
            if slot not in occupied_slots:
                return slot, floor
    return None, None

def confirm_parking():
    """Handle parking confirmation."""
    vehicle_type = vehicle_type_var.get()
    if not vehicle_type:
        messagebox.showerror("Error", "Please select a vehicle type!")
        return

    slot, floor = find_free_slot(vehicle_type)
    if slot:
        # Publish the occupied status to MQTT with error handling
        result = mqtt_client.publish(f"parking/{floor}/slot{slot}", "occupied", qos=1)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            messagebox.showerror("MQTT Publish Error", f"Failed to publish to topic parking/{floor}/slot{slot}")
        else:
            occupied_slots.add(slot)
            messagebox.showinfo("Parking Confirmed", f"Your parking spot is: {slot} on {floor}")
    else:
        messagebox.showwarning("No Slots Available", f"No free slots available for {vehicle_type}!")

def leave_parking():
    """Handle leaving parking."""
    vehicle_type = leave_vehicle_type_var.get()
    slot = selected_slot_var.get()

    if not vehicle_type:
        messagebox.showerror("Error", "Please select a vehicle type!")
        return

    if not slot:
        messagebox.showerror("Error", "Please select a slot!")
        return

    if slot in parking_slots[vehicle_type]["floor1"] or slot in parking_slots[vehicle_type]["floor2"]:
        # Determine the floor based on the selected slot
        floor = "floor1" if slot in parking_slots[vehicle_type]["floor1"] else "floor2"
        
        if slot in occupied_slots:
            # Publish the free status to MQTT with error handling
            result = mqtt_client.publish(f"parking/{floor}/slot{slot}", "free", qos=1)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                messagebox.showerror("MQTT Publish Error", f"Failed to publish to topic parking/{floor}/slot{slot}")
            else:
                occupied_slots.remove(slot)
                messagebox.showinfo("Left Parking", f"Slot {slot} on {floor} is now free.")
        else:
            messagebox.showerror("Error", "This slot is not currently occupied!")
    else:
        messagebox.showerror("Error", "This slot is not available for your vehicle type!")

def update_slot_options(*args):
    """Update the available slots in the 'Select Slot to Leave' dropdown based on selected vehicle type."""
    vehicle_type = leave_vehicle_type_var.get()
    
    # Clear the selected slot
    selected_slot_var.set('')  # This will clear the second dropdown
    
    if vehicle_type:
        available_slots = parking_slots[vehicle_type]["floor1"] + parking_slots[vehicle_type]["floor2"]
        # Update the dropdown with the slots corresponding to the selected vehicle type
        slot_dropdown['menu'].delete(0, 'end')
        for slot in available_slots:
            slot_dropdown['menu'].add_command(label=slot, command=tk._setit(selected_slot_var, slot))
    else:
        # If no vehicle type is selected, clear the dropdown
        slot_dropdown['menu'].delete(0, 'end')

# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_log = on_log
mqtt_client.on_publish = on_publish

# Connect to the broker with error handling
try:
    mqtt_client.connect(BROKER, PORT, 60)
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    messagebox.showerror("MQTT Error", f"Failed to connect to MQTT broker: {e}")
    exit(1)

# Start a background thread for the MQTT client to handle network traffic
mqtt_client.loop_start()

# Set up the GUI
root = tk.Tk()
root.title("Parking Manager")
root.geometry("400x400")

# Vehicle Type Selection for Confirming Parking
tk.Label(root, text="Select Vehicle Type (Confirm Parking):", font=("Arial", 12)).pack(pady=10)
vehicle_type_var = tk.StringVar()
vehicle_type_dropdown = tk.OptionMenu(root, vehicle_type_var, "electric", "motorcycle", "car")
vehicle_type_dropdown.pack(pady=5)

# Confirm Parking Button
confirm_button = tk.Button(root, text="Confirm Parking", command=confirm_parking, font=("Arial", 12), bg="green")
confirm_button.pack(pady=10)

# Leave Parking - Vehicle Type Selection
tk.Label(root, text="Select Vehicle Type (Leave Parking):", font=("Arial", 12)).pack(pady=10)
leave_vehicle_type_var = tk.StringVar()
leave_vehicle_type_var.trace("w", update_slot_options)  # Trigger update when vehicle type changes
leave_vehicle_type_dropdown = tk.OptionMenu(root, leave_vehicle_type_var, "electric", "motorcycle", "car")
leave_vehicle_type_dropdown.pack(pady=5)

# Slot Selection for Leaving Parking
tk.Label(root, text="Select Slot to Leave (Leave Parking):", font=("Arial", 12)).pack(pady=10)
selected_slot_var = tk.StringVar()
slot_dropdown = tk.OptionMenu(root, selected_slot_var, [])
slot_dropdown.pack(pady=5)

# Leave Parking Button
leave_button = tk.Button(root, text="Leave Parking", command=leave_parking, font=("Arial", 12), bg="red")
leave_button.pack(pady=10)

# Run the GUI event loop
root.mainloop()
