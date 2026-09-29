# AI-Interview-Assistant-training-tool-only-
AI Interview Assistant (training tool only)

## Moviola SDA — visualizzatore di algoritmi

`visualizer/index.html` è un visualizzatore passo passo per problemi in stile LeetCode.
Scrivi la soluzione in Python, premi **Esegui** e guarda l'esecuzione come un video:

- **array e stringhe** con i puntatori (`i`, `left`, `right`, `mid`, …) che scorrono sotto le celle e la finestra evidenziata
- **linked list** con le frecce `next` che cambiano direzione (inversione, merge, ciclo di Floyd)
- **alberi binari** con i nodi ancora nello stack di ricorsione colorati
- **grafi** (dict o lista di adiacenza) con i nodi visitati e in coda
- **matrici** (griglie, DP 2D), **hash map**, **set**, **stack**, **code**, **heap** (anche come albero)
- **stack delle chiamate** con le variabili di ogni frame e i valori di ritorno
- timeline con la profondità della ricorsione: clicca o trascina per saltare in qualsiasi punto

Controlli: `Spazio` play/pausa, `←` `→` un passo, clic sul numero di riga per saltare alla prossima
esecuzione di quella riga, rotellina per lo zoom, trascina per spostare strutture e nodi del grafo.

### Come si usa

Apri `visualizer/index.html` nel browser. Python gira nella pagina tramite
[Pyodide](https://pyodide.org), che viene scaricato da jsDelivr al primo avvio (serve la connessione).

### Sviluppo

I sorgenti sono in `visualizer/src/`:

- `tracer.py` esegue il codice con `sys.settrace` e registra stack e heap a ogni riga
- `template.html` contiene interfaccia, layout delle strutture e motore di animazione
- `examples.py` contiene gli esempi precaricati

Dopo una modifica rigenera la pagina:

```sh
python3 visualizer/build.py
```
