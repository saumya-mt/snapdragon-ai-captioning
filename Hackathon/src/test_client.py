from bleak import BleakClient, BleakScanner
import asyncio
import os

async def find_device():
    """Scan and find your device"""
    print("Scanning for devices...")
    devices = await BleakScanner.discover()
    
    for device in devices:
        if device.name == "Saumya":  # I can see this name in your server output
            print(f"Found your device! Address: {device.address}")
            return device.address
    return None

async def test_connection():
    # First find your device
    device_address = await find_device()
    
    if not device_address:
        print("Could not find your device. Make sure Bluetooth is on.")
        return
    
    print(f"Trying to connect to {device_address}...")
    try:
        async with BleakClient(device_address) as client:
            print("Connected!")
            
            # Send a test image
            test_image_path = "test_image.jpg"  # Make sure this file exists
            if not os.path.exists(test_image_path):
                print(f"Error: Test image not found at {test_image_path}")
                return
                
            with open(test_image_path, "rb") as f:
                image_data = f.read()
                
            # Send image
            await client.write_gatt_char(
                "image_characteristic_uuid",
                image_data
            )
            print("Image sent!")
            
            # Wait for response
            print("Waiting for response...")
            response = await client.read_gatt_char("audio_characteristic_uuid")
            
            # Save audio
            with open("response.mp3", "wb") as f:
                f.write(response)
            print("Response received and saved!")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 