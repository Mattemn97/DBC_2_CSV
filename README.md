# 🧩 DBC_2_CSV
**DBC_2_CSV** è un semplice ma potente script Python per convertire file **CAN DBC** in **CSV leggibili e modificabili**.  
Permette di estrarre tutti i segnali, con relativi attributi e tabelle di valori, in un formato tabellare facilmente analizzabile o importabile in altri strumenti.

## 🚀 Funzionalità principali
- ✅ Conversione completa dei file `.dbc` in `.csv`
- 📦 Supporto a messaggi, segnali, unità, scaling, offset e range
- 🧭 Estrazione di mittenti e ricevitori (ECU)
- 🔢 Conversione automatica dell’ID messaggio in formato **esadecimale**
- 📋 Inclusione delle **Value Table** come dizionari leggibili
- ⏳ Barra di avanzamento interattiva con **tqdm**
- 💬 Interfaccia testuale guidata: basta seguire le istruzioni a schermo

## 🧠 Requisiti
Assicurati di avere installato Python 3.8+ e i seguenti pacchetti:
```bash
pip install cantools tqdm
```
Il modulo csv e os sono parte della libreria standard Python.

## 🛠️ Utilizzo
1. Clona la repository:
```bash
git clone https://github.com/mattemn97/DBC_2_CSV.git
cd DBC_2_CSV
```

2. Esegui lo script:
```bash
python main.py
```

3. Segui le istruzioni a schermo:
* Inserisci il percorso completo del file .dbc
* Specifica dove salvare il file .csv di output

## 📄 Output generato

Il file CSV risultante usa come separatore il punto e virgola ; (compatibile con Excel e LibreOffice).
Ogni riga rappresenta un segnale con i seguenti campi:

| Colonna          | Descrizione                        |
| ---------------- | ---------------------------------- |
| Network          | Nome del bus (se presente nel DBC) |
| Message          | Nome del messaggio                 |
| Signal_Name      | Nome del segnale                   |
| Unit             | Unità di misura                    |
| Scaling_Factor   | Fattore di scala                   |
| Offset           | Offset                             |
| Min_Value        | Valore minimo                      |
| Max_Value        | Valore massimo                     |
| Default_Value    | Valore di default (se definito)    |
| ECU_Senders      | ECU mittenti                       |
| ECU_Receivers    | ECU riceventi                      |
| Value_Table      | Dizionario dei valori enumerati    |
| Message ID (hex) | ID messaggio in esadecimale        |
| Start Bit        | Bit di inizio del segnale          |
| Length (bit)     | Lunghezza del segnale in bit       |

## 🧩 Esempio di utilizzo
```bash
=== Convertitore DBC → CSV ===
Ti guiderò passo passo!

👉 Inserisci il percorso completo del file .dbc: C:\Dati\Rete_CAN.dbc
📂 Inserisci il percorso completo del file .csv da generare: C:\Output\Rete_CAN.csv

🔍 Sto leggendo il file DBC...
📊 Trovati 42 messaggi e 318 segnali totali.

🔧 Conversione in corso: 100%|█████████████████████████████| 318/318 [00:01<00:00, 295.00segnale/s]

✅ Conversione completata!
📄 File CSV generato in:
C:\Output\Rete_CAN.csv
```
