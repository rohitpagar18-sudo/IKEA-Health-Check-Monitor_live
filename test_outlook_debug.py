import win32com.client

print("Testing Outlook COM object...")
try:
    o = win32com.client.Dispatch('outlook.application')
    print(f"Outlook object type: {type(o)}")
    print(f"Outlook object: {o}")
    print(f"Has CreateItem: {hasattr(o, 'CreateItem')}")
    
    # Try to create a mail item
    print("Attempting to create mail item...")
    mail = o.CreateItem(0)
    print(f"Successfully created mail item: {type(mail)}")
except AttributeError as e:
    print(f"AttributeError: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
