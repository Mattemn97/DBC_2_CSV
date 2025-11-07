import cantools
import csv
import os
from tqdm import tqdm

def format_value_table(value_table):
    """Formatta il dizionario delle value table come stringa leggibile."""
    if not value_table:
        return 'N/A'
    return str({key: value for key, value in value_table.items()})

def dbc_to_csv():
    print("=== Convertitore DBC → CSV ===")
    print("Ti guiderò passo passo!\n")

    # Inserimento path DBC
    dbc_path = input("👉 Inserisci il percorso completo del file .dbc: ").strip()
    if not os.path.isfile(dbc_path):
        print("❌ Errore: file DBC non trovato.")
        return

    # Inserimento path CSV di output
    csv_path = input("📂 Inserisci il percorso completo del file .csv da generare: ").strip()
    csv_dir = os.path.dirname(csv_path)
    if csv_dir and not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    print("\n🔍 Sto leggendo il file DBC...")
    db = cantools.database.load_file(dbc_path)

    total_signals = sum(len(msg.signals) for msg in db.messages)
    print(f"📊 Trovati {len(db.messages)} messaggi e {total_signals} segnali totali.\n")

    # Apertura CSV e scrittura header
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow([
            'Network',
            'Message',
            'Signal_Name',
            'Unit',
            'Scaling_Factor',
            'Offset',
            'Min_Value',
            'Max_Value',
            'Default_Value',
            'ECU_Senders',
            'ECU_Receivers',
            'Value_Table',
            "Message ID (hex)",
            "Start Bit",
            "Length (bit)"
        ])

        # Conversione con barra di avanzamento
        with tqdm(total=total_signals, desc="🔧 Conversione in corso", unit="segnale", dynamic_ncols=True) as pbar:
            for msg in db.messages:
                for sig in msg.signals:
                    writer.writerow([
                        msg.bus_name or "N/A",                      # Network
                        msg.name,                                   # Message
                        sig.name,                                   # Signal name
                        sig.unit or "",                             # Unit
                        sig.scale,                                  # Scaling factor
                        sig.offset,                                 # Offset
                        sig.minimum,                                # Min value
                        sig.maximum,                                # Max value
                        getattr(sig, 'initial', ""),                # Default value (se presente)
                        ", ".join(msg.senders) if msg.senders else "",  # ECU senders
                        ", ".join(sig.receivers) if sig.receivers else "",  # ECU receivers
                        format_value_table(sig.choices),            # Value table
                        f"0x{msg.frame_id:X}",                      # Message ID (hex)
                        sig.start,                                  # Start bit
                        sig.length                                  # Length (bit)
                    ])
                    pbar.update(1)

    print(f"\n✅ Conversione completata!\n📄 File CSV generato in:\n{csv_path}")

if __name__ == "__main__":
    dbc_to_csv()
