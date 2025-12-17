from cantools import database
from pathlib import Path
from tqdm import tqdm
import csv


# ============================================================
# CLASSI DATI
# ============================================================

class ARR:
    HEADER = ["ID", "Values", "Unit"]

    def __init__(self, Id, Values, Unit):
        self.Id = Id
        # Manteniamo il tuo appiattimento (senza virgole) per evitare confusione dentro al campo.
        self.Values = str(Values).replace('[', '').replace(']', '').replace('\'', '').replace(',', '')
        self.Unit = Unit

    def to_row(self):
        return [self.Id, self.Values, self.Unit]


class VTB:
    HEADER = ["ID", "Descriptive_Name", "Simulink_Name", "ARR_ID_Input", "ARR_ID_Output"]

    def __init__(self, Id, Descriptive_Name, Simulink_Name, ARR_ID_Input, ARR_ID_Output):
        self.Id = Id
        self.Descriptive_Name = Descriptive_Name
        self.Simulink_Name = Simulink_Name
        self.ARR_ID_Input = ARR_ID_Input
        self.ARR_ID_Output = ARR_ID_Output

    def to_row(self):
        return [self.Id, self.Descriptive_Name, self.Simulink_Name, self.ARR_ID_Input, self.ARR_ID_Output]


class CAN:
    HEADER = [
        "ID", "Network", "Message", "Descriptive_Name", "Simulink_Name", "Offset", "Scaling_Factor",
        "Min_Value", "Max_Value", "Default_Value", "Unit", "SPN", "ECU_Receivers", "ECU_Senders",
        "VTB_ID", "INP_ID", "OUT_ID"
    ]

    def __init__(
        self, Id, Network, Message, Descriptive_Name, Simulink_Name,
        Offset, Scaling_Factor, Min_Value, Max_Value, Default_Value,
        Unit, SPN, ECU_Receivers, ECU_Senders, VTB_ID, INP_ID, OUT_ID
    ):
        self.Id = Id
        self.Network = Network
        self.Message = Message
        self.Descriptive_Name = Descriptive_Name
        self.Simulink_Name = Simulink_Name
        self.Offset = Offset
        self.Scaling_Factor = Scaling_Factor
        self.Min_Value = Min_Value
        self.Max_Value = Max_Value
        self.Default_Value = Default_Value
        self.Unit = Unit
        self.SPN = SPN
        # Manteniamo l'appiattimento (senza virgole) come in origine.
        self.ECU_Receivers = str(ECU_Receivers).replace('[', '').replace(']', '').replace('\'', '').replace(',', '')
        self.ECU_Senders = str(ECU_Senders).replace('[', '').replace(']', '').replace('\'', '').replace(',', '')
        self.VTB_ID = VTB_ID
        self.INP_ID = INP_ID
        self.OUT_ID = OUT_ID

    def to_row(self):
        # >>> Formattazione locale dei numeri con la virgola come separatore dei decimali
        def fmt_num(v):
            if v is None:
                return "NA"
            # Conserviamo gli interi, per i float cambiamo il punto in virgola
            if isinstance(v, (int, float)):
                s = str(v)
                # Non aggiungiamo separatori migliaia; solo sostituzione del separatore decimale
                return s.replace('.', ',')
            # Qualsiasi altro tipo passa come stringa
            return str(v)

        return [
            self.Id,
            self.Network,
            self.Message,
            self.Descriptive_Name,
            self.Simulink_Name,
            fmt_num(self.Offset),
            fmt_num(self.Scaling_Factor),
            fmt_num(self.Min_Value),
            fmt_num(self.Max_Value),
            fmt_num(self.Default_Value),
            self.Unit,
            self.SPN,
            self.ECU_Receivers,
            self.ECU_Senders,
            self.VTB_ID,
            self.INP_ID,
            self.OUT_ID,
        ]


# ============================================================
# UTILS
# ============================================================

def scrittura_csv(file_path: Path, header, rows):
    """
    Scrive CSV con delimitatore ';' (punto e virgola) e BOM UTF-8 per Excel italiano.
    """
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        print(f"Scrivendo: {file_path.name}")
        writer = csv.writer(f, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Scritto: {file_path.name}")


def normalize_choices(choices: dict):
    """
    Ordina determinist. per chiave numerica e ritorna lista di (key_int, value_str)
    """
    items = []
    for k, v in choices.items():
        key_int = int(k)
        value_str = v.name if hasattr(v, "name") else str(v)
        items.append((key_int, value_str))
    items.sort(key=lambda t: t[0])
    return items


# ============================================================
# CORE
# ============================================================

def elabora_dbc(dbc_path: Path, out_can: Path, out_vtb: Path, out_arr: Path):
    lista_CAN = []
    lista_VTB = []
    lista_ARR = []

    # Cache per deduplica effettiva
    vtb_cache = {}        # (arr_in_key, arr_out_key) -> VTB_ID
    arr_in_cache = {}     # arr_in_key  (tuple[int]) -> ARR_IN_ID
    arr_out_cache = {}    # arr_out_key (tuple[str]) -> ARR_OUT_ID

    iter_CAN = 0
    iter_VTB = 0
    iter_ARR = 0

    can_db = database.load_file(dbc_path)

    total_signals = sum(len(msg.signals) for msg in can_db.messages)
    print(f"📊 Trovati {len(can_db.messages)} messaggi e {total_signals} segnali.\n")

    with tqdm(total=total_signals, desc="🔧 Conversione in corso", unit="segnale", dynamic_ncols=True) as pbar:
        for messaggio in can_db.messages:
            for segnale in messaggio.signals:
                iter_CAN += 1
                str_key_CAN = f"CAN_{str(iter_CAN).zfill(4)}"
                str_key_VTB = "NA"
                arr_in_id = "NA"
                arr_out_id = "NA"

                if segnale.choices:
                    items = normalize_choices(segnale.choices)
                    arr_in_key = tuple(k for k, _ in items)         # es. (0,1,2,3)
                    arr_out_key = tuple(v for _, v in items)        # es. ("Off","On",...)
                    vtb_key = (arr_in_key, arr_out_key)

                    if vtb_key in vtb_cache:
                        # Riutilizzo VTB e ARR esistenti
                        str_key_VTB = vtb_cache[vtb_key]
                        arr_in_id = arr_in_cache[arr_in_key]
                        arr_out_id = arr_out_cache[arr_out_key]
                    else:
                        # ARR IN dedup
                        if arr_in_key in arr_in_cache:
                            arr_in_id = arr_in_cache[arr_in_key]
                        else:
                            iter_ARR += 1
                            arr_in_id = f"ARR_{str(iter_ARR).zfill(4)}"
                            lista_ARR.append(ARR(arr_in_id, list(arr_in_key), "NA"))
                            arr_in_cache[arr_in_key] = arr_in_id

                        # ARR OUT dedup
                        if arr_out_key in arr_out_cache:
                            arr_out_id = arr_out_cache[arr_out_key]
                        else:
                            iter_ARR += 1
                            arr_out_id = f"ARR_{str(iter_ARR).zfill(4)}"
                            lista_ARR.append(ARR(arr_out_id, list(arr_out_key), "NA"))
                            arr_out_cache[arr_out_key] = arr_out_id

                        # Crea nuova VTB riusando gli ARR
                        iter_VTB += 1
                        str_key_VTB = f"VTB_{str(iter_VTB).zfill(4)}"
                        lista_VTB.append(VTB(str_key_VTB, "NA", "NA", arr_in_id, arr_out_id))
                        vtb_cache[vtb_key] = str_key_VTB

                # ---------- CAN ----------
                lista_CAN.append(
                    CAN(
                        str_key_CAN,
                        getattr(messaggio, "bus_name", "NA"),
                        messaggio.name,
                        segnale.name,
                        "NA",                              # Descriptive_Name per ora NA
                        segnale.offset,
                        segnale.scale,
                        segnale.minimum,
                        segnale.maximum,
                        segnale.initial,
                        segnale.unit,
                        getattr(segnale, "spn", "NA"),
                        getattr(segnale, "receivers", "NA"),
                        getattr(messaggio, "senders", "NA"),
                        str_key_VTB,
                        arr_in_id,
                        arr_out_id
                    )
                )

                pbar.update(1)

    # Scrittura file con delimitatore ';' e numeri localizzati
    if lista_CAN:
        scrittura_csv(out_can, CAN.HEADER, [c.to_row() for c in lista_CAN])
    if lista_VTB:
        scrittura_csv(out_vtb, VTB.HEADER, [v.to_row() for v in lista_VTB])
    if lista_ARR:
        scrittura_csv(out_arr, ARR.HEADER, [a.to_row() for a in lista_ARR])


# ============================================================
# MENU + MAIN
# ============================================================

def menu():
    dbc_path = Path(input("👉 Inserisci il percorso completo del file .dbc: ").strip())

    if not dbc_path.is_file() or dbc_path.suffix.lower() != ".dbc":
        print("❌ File DBC non valido.")
        return None

    base_dir = dbc_path.parent
    base_name = dbc_path.stem

    return (
        dbc_path,
        base_dir / f"{base_name}_CAN.csv",
        base_dir / f"{base_name}_VTB.csv",
        base_dir / f"{base_name}_ARR.csv",
    )


def main():
    result = menu()
    if result is None:
        return

    elabora_dbc(*result)


if __name__ == "__main__":
    main()
