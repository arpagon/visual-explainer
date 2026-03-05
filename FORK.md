# Fork: arpagon/visual-explainer

## Origen

Fork de [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) — un skill de agente que convierte salida compleja de terminal en páginas HTML estilizadas y autocontenidas.

## Cómo funciona

```
upstream/main          ← nicobailon/visual-explainer
       │
       │  sync.sh (fetch + copiar archivos)
       ▼
  SKILL.md upstream puro
       │
       │  El agente lee preferences.yaml y aplica cambios
       ▼
     main              ← única rama: upstream + preferencias aplicadas
```

Sin parches mecánicos. El agente lee `preferences.yaml`, entiende la intención, y edita `SKILL.md` con criterio. Si upstream reescribe una sección, el agente se adapta.

### Sincronizar

Decirle al agente: **"actualiza visual-explainer y aplica mis preferencias"**

O manualmente:
```bash
bash .arpagon/sync.sh   # trae upstream
# luego el agente lee preferences.yaml y aplica
```

## Preferencias

Definidas en `.arpagon/preferences.yaml`:

| Preferencia | Intención |
|------------|-----------|
| `opt-in-only` | Quitar todo comportamiento proactivo — solo activar cuando el usuario lo pida |
| `agent-browser` | Reemplazar surf-cli con agent-browser para screenshots web |
| `gcs-upload` | Reemplazar sharing via Vercel con upload a GCS |

## Archivos custom

Copiados desde `.arpagon/files/` durante el sync:

| Archivo | Reemplaza |
|---------|-----------|
| `scripts/upload.py` | `scripts/share.sh` |
| `commands/share.md` | Versión Vercel de upstream |

## Branching

Una rama: `main`. Eso es todo.

- `main` = upstream + preferencias aplicadas (lo que pi lee)
- `remotes/upstream/main` = referencia upstream (via `git fetch upstream`)

## Estructura

```
.arpagon/
├── preferences.yaml      ← Qué quiero (el agente lee esto)
├── sync.sh               ← Trae archivos de upstream
└── files/                 ← Archivos custom copiados durante sync
    ├── scripts/upload.py
    └── commands/share.md
```
