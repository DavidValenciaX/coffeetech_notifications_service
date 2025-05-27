# Guía de Migración: Integración de Entidades

## Estrategia de Migración Recomendada

### ❌ **NO hagas esto:**
- Eliminar `notification_service.py` inmediatamente
- Cambiar todos los endpoints de una vez
- Hacer cambios masivos sin testing

### ✅ **SÍ haz esto:**
- Migración gradual y controlada
- Mantener compatibilidad durante la transición
- Testing exhaustivo en cada paso

## Pasos de Migración

### Paso 1: Preparación (Ya completado ✅)
- [x] Crear entidades en `domain/entities/`
- [x] Crear mapper para conversión
- [x] Crear tests unitarios
- [x] Crear servicio mejorado

### Paso 2: Actualizar Endpoints (Recomendado)

#### 2.1 Verificar qué endpoints usan el servicio actual

```bash
# Buscar referencias al servicio actual
grep -r "NotificationService" endpoints/
```

#### 2.2 Actualizar imports en endpoints

**Antes:**
```python
from domain.services.notification_service import NotificationService
```

**Después:**
```python
from domain.services.notification_service_enhanced import NotificationServiceEnhanced as NotificationService
```

#### 2.3 Archivos que necesitan actualización

Basado en el análisis del código, estos son los archivos que usan `NotificationService`:

1. **Endpoints:**
   - `endpoints/internal/notifications_internal.py`
   - `endpoints/external/notifications_external.py`

2. **Use Cases:**
   - `use_cases/get_notifications_use_case.py`

3. **Tests:**
   - `tests/use_cases/test_get_notifications_use_case.py`

#### 2.4 Actualización de endpoints internos

**Archivo:** `endpoints/internal/notifications_internal.py`

**Cambio mínimo (Opción 1 - Recomendada):**
```python
# Línea 8: Cambiar el import
from domain.services.notification_service_enhanced import NotificationServiceEnhanced as NotificationService, NotificationNotFoundError

# El resto del código permanece igual
```

**Cambio completo (Opción 2):**
```python
# Línea 8: Cambiar el import
from domain.services.notification_service_enhanced import NotificationServiceEnhanced, NotificationNotFoundError

# Línea 16: Cambiar el tipo de retorno
def get_notification_service(db: Session = Depends(get_db_session)) -> NotificationServiceEnhanced:
    repository = NotificationRepository(db)
    return NotificationServiceEnhanced(repository)

# Línea 22 y siguientes: Cambiar el tipo del parámetro
def get_notification_states(service: NotificationServiceEnhanced = Depends(get_notification_service)):
    # ... resto del código igual
```

#### 2.5 Actualización de endpoints externos

**Archivo:** `endpoints/external/notifications_external.py`

**Cambio:**
```python
# Línea 5: Cambiar el import
from domain.services.notification_service_enhanced import NotificationServiceEnhanced as NotificationService

# Línea 73: El código permanece igual
notification_service = NotificationService(notification_repository)
```

#### 2.6 Actualización de use cases

**Archivo:** `use_cases/get_notifications_use_case.py`

**Cambio:**
```python
# Línea 2: Cambiar el import
from domain.services.notification_service_enhanced import NotificationServiceEnhanced as NotificationService

# El resto del código permanece igual
```

### Paso 3: Testing de la Migración

#### 3.1 Ejecutar tests existentes
```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Ejecutar tests específicos de notificaciones
python -m pytest tests/use_cases/test_get_notifications_use_case.py -v
```

#### 3.2 Probar endpoints manualmente
```bash
# Probar endpoint de estados
curl -X GET "http://localhost:8000/internal/notifications/states"

# Probar endpoint de tipos
curl -X GET "http://localhost:8000/internal/notifications/types"

# Probar endpoint de notificaciones de usuario
curl -X GET "http://localhost:8000/external/notifications/user/123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Paso 4: Validación de Funcionalidad

#### 4.1 Verificar que las entidades funcionan correctamente
```python
# Test rápido en Python shell
from domain.entities import Notification
from domain.services.notification_service_enhanced import NotificationServiceEnhanced

# Crear notificación de prueba
notification = Notification.create_new(
    message="Test",
    user_id=1,
    notification_type_id=1,
    invitation_id=1,
    notification_state_id=1
)

print(f"Notification created: {notification}")
print(f"Is pending: {notification.is_pending()}")
```

#### 4.2 Verificar logs
- Revisar que los logs muestren el uso de entidades
- Verificar que las validaciones funcionan correctamente
- Confirmar que los estados se actualizan apropiadamente

### Paso 5: Limpieza (Opcional)

Una vez que todo funcione correctamente:

#### 5.1 Renombrar archivos
```bash
# Respaldar el servicio original
mv domain/services/notification_service.py domain/services/notification_service_old.py

# Renombrar el servicio mejorado
mv domain/services/notification_service_enhanced.py domain/services/notification_service.py
```

#### 5.2 Actualizar imports de vuelta
```python
# Cambiar de vuelta a:
from domain.services.notification_service import NotificationService
```

#### 5.3 Eliminar archivos temporales
```bash
# Después de confirmar que todo funciona
rm domain/services/notification_service_old.py
rm domain/services/notification_service_with_entity.py  # Archivo de ejemplo
```

## Ventajas de esta Migración

### ✅ **Beneficios Inmediatos:**
1. **Validación automática**: Las entidades validan datos automáticamente
2. **Mejor manejo de errores**: Errores más específicos y claros
3. **Código más expresivo**: Métodos como `is_pending()`, `mark_as_sent()`
4. **Lógica centralizada**: Reglas de negocio en un solo lugar

### ✅ **Beneficios a Largo Plazo:**
1. **Mantenibilidad**: Cambios en lógica de negocio centralizados
2. **Testabilidad**: Fácil testing de lógica de negocio
3. **Extensibilidad**: Fácil agregar nuevas reglas y validaciones
4. **Independencia**: No depende de frameworks específicos

## Rollback Plan

Si algo sale mal:

1. **Rollback inmediato:**
   ```bash
   # Cambiar imports de vuelta
   git checkout -- endpoints/
   git checkout -- use_cases/
   ```

2. **Rollback completo:**
   ```bash
   # Restaurar servicio original
   git checkout HEAD~1 domain/services/notification_service.py
   ```

## Checklist de Migración

- [ ] Backup del código actual
- [ ] Actualizar imports en endpoints internos
- [ ] Actualizar imports en endpoints externos  
- [ ] Actualizar imports en use cases
- [ ] Ejecutar tests unitarios
- [ ] Probar endpoints manualmente
- [ ] Verificar logs de aplicación
- [ ] Confirmar que FCM sigue funcionando
- [ ] Validar que las notificaciones se crean correctamente
- [ ] Verificar que los estados se actualizan
- [ ] Documentar cambios realizados

## Recomendación Final

**Usa la Opción 1 (cambio mínimo)** para la migración inicial:

```python
from domain.services.notification_service_enhanced import NotificationServiceEnhanced as NotificationService
```

Esto te permite:
- ✅ Usar las entidades inmediatamente
- ✅ Mantener compatibilidad total
- ✅ Rollback fácil si hay problemas
- ✅ Testing gradual de la nueva funcionalidad 