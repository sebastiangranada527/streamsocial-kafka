# Cómo contribuir a StreamSocial

## Estrategia de Branches

Usamos el modelo **Gitflow simplificado**:

```
main          ← producción, solo merge via PR desde develop
develop       ← integración, base para nuevas features
feature/*     ← una branch por fase o funcionalidad
```

**Ejemplo:**
```bash
git checkout develop
git checkout -b feature/fase-2-event-models
# ... trabajar ...
git push origin feature/fase-2-event-models
# Abrir PR hacia develop
```

## Reglas de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat:     nueva funcionalidad
fix:      corrección de bug
docs:     cambios en documentación
test:     agregar o modificar tests
chore:    tareas de mantenimiento (deps, config)
refactor: refactorización sin cambio de comportamiento
```

**Ejemplos:**
```bash
git commit -m "feat: agregar producer de eventos Kafka"
git commit -m "fix: corregir serialización de timestamp en eventos"
git commit -m "test: agregar tests unitarios para StreamSocialEvent"
```

## Antes de abrir un PR

- [ ] Los tests pasan localmente (`make test`)
- [ ] El linter no reporta errores (`make lint`)
- [ ] El PR tiene título descriptivo y descripción del cambio
- [ ] Se actualizó documentación si aplica
