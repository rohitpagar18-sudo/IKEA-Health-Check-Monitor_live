import win32com.client as win32

outlook = win32.Dispatch('outlook.application')
mail = outlook.CreateItem(0)
mail.To = 'Rohit.AvinashPagar@cognizant.com'
mail.Subject = 'Test Email from Python'
mail.Body = 'This is a test email sent from Python using win32com.'
mail.Send()
print("Sent!")