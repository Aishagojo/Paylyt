import customtkinter as ctk
import requests
import json
import webbrowser

# --- BACKEND CONFIGURATION ---
API_URL = "https://api.coingecko.com/api/v3/simple/price"
SATS_PER_BTC = 100_000_000

def get_btc_price(currency="usd"):
    """Fetches the current Bitcoin price in the specified currency."""
    params = {
        'ids': 'bitcoin',
        'vs_currencies': currency.lower()
    }
    try:
        # Use a short timeout to prevent the UI from freezing indefinitely
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        price = data.get('bitcoin', {}).get(currency.lower())
        return price
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: Failed to fetch price for {currency.upper()}: {e}")
        return None
# ----------------------------------------------------------------

class SatoshiConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Basic App Setup
        self.title("⚡ Haraka Sats (Quick-Check)")
        self.geometry("450x570") 
        self.resizable(False, False)
        ctk.set_appearance_mode("System") 
        ctk.set_default_color_theme("blue")
        
        # Internal variables for price caching
        self.btc_price_usd = None
        self.btc_price_kes = None

        # 2. Widget Definitions
        
        # Current Price Display (Updated to be more prominent)
        self.price_label = ctk.CTkLabel(
            self, 
            text="Loading Price Data...", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#F7931A" 
        )
        self.price_label.pack(pady=20, padx=10)

        # Input Label
        self.input_label = ctk.CTkLabel(
            self, 
            text="Enter Satoshis (sats):",
            font=ctk.CTkFont(size=14)
        )
        self.input_label.pack(pady=(10, 0))

        # Input Field
        self.sats_entry = ctk.CTkEntry(
            self, 
            width=250, 
            height=40, 
            font=ctk.CTkFont(size=20),
            placeholder_text="e.g., 50000"
        )
        self.sats_entry.pack(pady=10)

        # Output Label (for conversion result)
        self.result_label = ctk.CTkLabel(
            self, 
            text="Value: ---", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.result_label.pack(pady=30)
        
        # Currency Buttons Frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=10, fill="x")
        
        # KES Button
        self.kes_button = ctk.CTkButton(
            self.button_frame, 
            text="Convert to KES (Ksh)", 
            command=lambda: self.convert_sats('kes'),
            fg_color="#008000", # Green for KES
            hover_color="#006400"
        )
        self.kes_button.pack(side="top", padx=15, pady=10, expand=True, fill="x")

        # USD Button
        self.usd_button = ctk.CTkButton(
            self.button_frame, 
            text="Convert to USD ($)", 
            command=lambda: self.convert_sats('usd'),
            fg_color="#30A852",
            hover_color="#247C3E"
        )
        self.usd_button.pack(side="left", padx=(15, 10), pady=10, expand=True)

        # EUR Button
        self.eur_button = ctk.CTkButton(
            self.button_frame, 
            text="Convert to EUR (€)", 
            command=lambda: self.convert_sats('eur'),
            fg_color="#0064C8",
            hover_color="#004D99"
        )
        self.eur_button.pack(side="right", padx=(10, 15), pady=10, expand=True)
        
        # 3. Donation Section
        self.donation_frame = ctk.CTkFrame(self)
        self.donation_frame.pack(pady=(15, 10), padx=10, fill="x")
        
        self.donate_label = ctk.CTkLabel(
            self.donation_frame, 
            text="🤝 Support Human Rights & Fight GBV", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.donate_label.pack(pady=(10, 5))

        self.donate_button = ctk.CTkButton(
            self.donation_frame,
            text="Donate Sats via Lightning Address",
            command=self.donate_sats,
            fg_color="#E20F91", 
            hover_color="#F00B98"
        )
        self.donate_button.pack(pady=(5, 10), padx=15, fill="x")

        # 4. ERROR FIX: Defer the initial price fetch using self.after()
        # This ensures the Tkinter environment is fully set up before updating widgets.
        self.after(100, self.update_price_display) 

    def update_price_display(self):
        """Fetches and displays the current BTC price in USD and KES."""
        self.btc_price_usd = get_btc_price('usd')
        self.btc_price_kes = get_btc_price('kes') 
        
        if self.btc_price_usd and self.btc_price_kes:
            self.price_label.configure(
                text=f"LIVE PRICE:\n1 BTC = ${self.btc_price_usd:,.2f} USD\n1 BTC = Ksh {self.btc_price_kes:,.2f} KES"
            )
        else:
            self.price_label.configure(text="PRICE FAILED TO LOAD.\nCheck your internet connection.", text_color="red")
            self.usd_button.configure(state="disabled")
            self.eur_button.configure(state="disabled")
            self.kes_button.configure(state="disabled")

    def convert_sats(self, currency):
        """Performs the conversion and updates the result label."""
        try:
            sats_text = self.sats_entry.get().replace(',', '').strip()
            if not sats_text:
                 self.result_label.configure(text="Value: Please enter satoshis.")
                 return
                 
            sats = int(sats_text)
            
            if sats < 0:
                self.result_label.configure(text="Value: Enter a positive number.")
                return

        except ValueError:
            self.result_label.configure(text="Value: Invalid input. Use whole numbers.")
            return

        # Use cached price if available, otherwise fetch it.
        if currency == 'usd' and self.btc_price_usd:
            price = self.btc_price_usd
        elif currency == 'kes' and self.btc_price_kes:
            price = self.btc_price_kes
        else:
            price = get_btc_price(currency)
        
        if price is None:
            self.result_label.configure(text=f"Value: Failed to get {currency.upper()} price.")
            return

        # 3. Calculate conversion
        btc_amount = sats / SATS_PER_BTC
        fiat_value = btc_amount * price
        
        # 4. Format and display
        if currency == 'usd':
            format_str = f"${fiat_value:,.4f} USD"
        elif currency == 'eur':
            format_str = f"€{fiat_value:,.4f} EUR"
        elif currency == 'kes':
            format_str = f"Ksh {fiat_value:,.2f} KES" # Ksh with 2 decimals
        else:
            format_str = f"{fiat_value:,.4f} {currency.upper()}"
            
        self.result_label.configure(text=f"Value: {format_str}")

    def donate_sats(self):
        """Opens a link to facilitate a Lightning donation."""
        lightning_address = "hrf@btcpay.hrf.org"
        covaw_link = "https://covaw.or.ke/get-involved/donate/"
        
        message = (
            f"Thank you for your generosity! To donate Satoshis, "
            f"copy the Human Rights Foundation's Lightning Address below:\n\n"
            f"👉 **{lightning_address}**\n\n"
            f"We also recommend checking out COVAW (Coalition on Violence Against Women) for local support in Kenya."
        )
        
        # Use a CustomTkinter Message Box (not the input dialog) to display the donation information
        # and then open the link upon confirmation.
        
        # Note: ctk.CTkInputDialog is for text input, ctk.CTkMessagebox (if available/imported) 
        # or a simple TK toplevel is preferred for just displaying info. 
        # For simplicity and robust display, we'll use a standard print and open the web browser.
        
        print(f"\n--- DONATION DETAILS ---")
        print(f"Lightning Address (Copy and Paste): {lightning_address}")
        print(f"Opening COVAW link: {covaw_link}")
        print(f"------------------------\n")

        # Open the browser link to the local organization
        webbrowser.open_new(covaw_link)


if __name__ == "__main__":
    app = SatoshiConverterApp()
    app.mainloop()