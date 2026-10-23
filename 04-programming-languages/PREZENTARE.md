# Prezentare salestools - ordinea, ce spun, ce rulez

## 0. Inainte sa incep (pregatire, 2 minute)

```bash
cd ~/Downloads/Review/04-programming-languages
source .venv/bin/activate              # fish: source .venv/bin/activate.fish
which python                           # trebuie sa contina .venv
pip install -e ".[dev]"                # daca nu e deja instalat
ruff check . && python -m pytest       # sa stiu ca totul e verde inainte sa incep
```

Daca `pytest` zice `No module named salestools`: nu sint in venv. Activez venv-ul si folosesc `python -m pytest`.

Deschis in editor, in ordinea asta: `README.md`, `cleaning.py`, `report.py`, `discounts.py`, `tests/`, `debug_demo.py`, `pyproject.toml`.

---

## 1. Ordinea fisierelor si ce spun

### 1) README.md (30 secunde)
**Spun:** "Este un pachet Python mic care curata rinduri de vanzari, face un raport comprimat, aplica discounturi si converteste valuta. L-am facut ca sa exersez cod curat, teste si impachetare."
**Arat:** lista de fisiere din README.

### 2) src/salestools/cleaning.py (1-2 minute)
**Spun:**
- "Aici curat sumele cu o expresie regulata (`re`) si datele cu `datetime`. Accept mai multe formate de data."
- "Folosesc constructii de baza: `if`, `for`, liste si dictionare, si `try/except`."
- "Am o exceptie proprie, `InvalidRowError`. Un rind gresit nu opreste restul: ajunge in lista `bad`, cu motivul."
- "Numele sint in snake_case, exista docstring-uri, urmez PEP 8."
**Rulez:**
```bash
ruff check .                           # ghid de stil: "All checks passed!"
python -m salestools data/sales.csv    # 4 rinduri bune, 3 respinse + rezumat
```

### 3) src/salestools/report.py (1 minut)
**Spun:** "Aici folosesc biblioteca standard: `csv` pentru citire, `gzip` si `json` pentru raportul comprimat, `pathlib` pentru cai, `statistics` pentru media si mediana. N-am scris nimic de mina pentru lucrurile astea."
**Arat:** fisierul creat dupa rulare: `ls out/` si `python -c "import gzip,json;print(json.load(gzip.open('out/clean.json.gz','rt')))"`

### 4) src/salestools/discounts.py (1 minut)
**Spun:** "Aici am folosit pattern-ul Strategy. Regula de discount se schimba (fara, procent, prag), dar codul care aduna totalul ramine la fel. Fiecare regula e o clasa cu aceeasi metoda `apply()`. `get_discount` alege regula dupa nume, e un factory simplu. Daca vreau o regula noua, adaug o clasa si o linie in `RULES`."
**Rulez:**
```bash
python -c "from salestools.discounts import get_discount, total_after_discount; print(total_after_discount([100, 50], get_discount('percent', percent=10)))"
```
Rezultat: `135.0`.

### 5) tests/ (2-3 minute)
**Spun:**
- "`test_cleaning.py`, `test_discounts.py`, `test_report.py`: teste unitare cu asertiuni. Acolo unde aceeasi logica are multe intrari, folosesc teste parametrizate (`@pytest.mark.parametrize`), ca sa nu repet codul."
- "`test_report.py` are `setup_method` si `teardown_method`, ca sa pregatesc si sa curat fisierele de test."
- "`test_rates.py` foloseste un stub si un mock: doar `rates.py` apeleaza reteaua, deci in teste inlocuiesc `fetch_rates` cu un raspuns fix si `urlopen` cu un Mock, ca sa verific cum a fost apelat. Testele nu merg niciodata pe internet."
**Rulez:**
```bash
python -m pytest
```
Ma uit la: numarul de teste trecute, tabelul de coverage si linia "Required test coverage of 90% reached".

**Povestea de coverage (Middle):**
```bash
python -m pytest tests/test_cleaning.py     # "inainte": sub prag, arata liniile lipsa
python -m pytest                            # "dupa": toate testele
```
Spun: "Am vazut ce linii nu erau acoperite (coloana Missing) si am scris teste pentru ele. De exemplu `__main__.py` era la 0%, pentru ca rula doar la pornirea pachetului; am adaugat un test care il porneste."
(Testul pentru `__main__.py` e in sectiunea 4. Il pun doar daca l-am adaugat si trece.)

### 6) debug_demo.py (1-2 minute)
**Spun:** "Este un exercitiu de debugging. Am o functie cu un bug: crapa cind o valoare e `None`. Am folosit logging pe niveluri (DEBUG, INFO, ERROR) si un breakpoint, ca sa gasesc cauza metodic."
**Rulez:**
```bash
python debug_demo.py                   # se vede ERROR cu traceback, apoi DEBUG si INFO pentru versiunea reparata
```
Apoi decomentez `# breakpoint()` in functia `average`, rulez din nou si folosesc: `n` (urmatoarea linie), `p total`, `p row`, `c` (continua), `q` (iesire).
**Spun:** "Am gasit ca al treilea rind are `amount=None`, iar suma nu poate aduna `int` cu `None`. In `average_fixed` filtrez valorile lipsa si loghez cite rinduri folosesc."
(Sincer: bug-ul e pus de mine intentionat, ca exercitiu.)

### 7) pyproject.toml (1 minut)
**Spun:** "Aici declar pachetul: nume, versiune, dependintele (`dev`: pytest, pytest-cov, ruff), setarile pentru pytest si ruff. Managerul de pachete e `pip`, in mediu virtual, iar manifestul e `pyproject.toml`."
**Rulez:**
```bash
pip list | grep -i -E "salestools|pytest|ruff"
python -m build                        # dist/salestools-0.1.0-py3-none-any.whl
python -m venv /tmp/test-env
/tmp/test-env/bin/pip install dist/salestools-0.1.0-py3-none-any.whl
cd /tmp && /tmp/test-env/bin/python -m salestools ~/Downloads/Review/04-programming-languages/data/sales.csv
```
**Spun:** "Pachetul se construieste intr-un wheel si se instaleaza intr-un mediu separat, fara codul sursa."
(Daca `build` lipseste: `pip install build`. Ajusteaza calea catre `sales.csv`.)

---

## 2. Rezumat task -> dovada (de tinut la indemina)

| Task | Dovada |
|---|---|
| Ghid de stil | `ruff check .` -> "All checks passed!" |
| Constructii de baza | `cleaning.py` |
| Teste unitare | `python -m pytest`, `setup_method`/`teardown_method` in `test_report.py` |
| Debugging | `debug_demo.py`: logging + breakpoint |
| Package manager | `pyproject.toml` + `pip install -e ".[dev]"` |
| Standard library | `re`, `datetime`, `csv`, `gzip`, `json`, `statistics`, `pathlib`, `urllib` |
| Acoperire cu teste | tabelul de coverage, inainte/dupa |
| Design patterns | `discounts.py` (Strategy + factory) |
| Teste parametrizate | `@pytest.mark.parametrize` |
| Pachet distribuit | wheel construit si instalat in alt venv |
| Stubs si mocks | `tests/test_rates.py` |

---

## 3. Fixuri si completari (daca nu sint facute deja)

**`pytest` nu gaseste pachetul fara instalare.** In `pyproject.toml`, la `[tool.pytest.ini_options]`, adaug:
```toml
pythonpath = ["src"]
```

**Coverage pe `__main__.py`.** Creez `tests/test_main.py`:
```python
import runpy
import sys


def test_main_runs(tmp_path, monkeypatch, capsys):
    csv_path = tmp_path / "s.csv"
    csv_path.write_text(
        "order_id,customer_id,category,amount,date\n"
        "1,1,books,10,2026-10-01\n"
        "2,1,toys,abc,2026-10-01\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["salestools", str(csv_path)])
    runpy.run_module("salestools.__main__", run_name="__main__")
    assert (tmp_path / "out" / "clean.json.gz").exists()
    assert "good=1 bad=1" in capsys.readouterr().out
```
Dupa asta rulez `python -m pytest` si notez noul procent. (Testul nu a fost rulat de cel care l-a scris, deci verific ca trece.)

**Dupa `ruff format`.** Rulez din nou `python -m pytest`, sa ma asigur ca nimic nu s-a stricat.

---

## 4. Daca ma intreaba

- **"De ce Strategy?"** - regula de discount se schimba, restul codului nu.
- **"Cit e coverage-ul?"** - citesc cifra din raport (la ultima rulare am vazut 91.59%, cu `__main__.py` la 0% inainte de test).
- **"De ce mock la `urlopen`?"** - ca testele sa nu depinda de retea si sa fie rapide si deterministe.
- **"Bug-ul din debug_demo e real?"** - nu, l-am pus intentionat ca exercitiu.
- **"Unde se foloseste `discounts.py`?"** - e o biblioteca; o folosesc din cod, iar testele o exerseaza.
