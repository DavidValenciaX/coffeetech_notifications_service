# Implementación de la Entidad Notification

## Resumen

Se ha implementado exitosamente la entidad `Notification` en la capa de dominio del servicio de notificaciones, siguiendo los principios de Domain-Driven Design (DDD) y Clean Architecture.

## Archivos Creados

### 1. Estructura de Entidades
```
domain/entities/
├── __init__.py                           # Exporta Notification y NotificationMapper
├── notification.py                       # Entidad principal Notification
├── notification_mapper.py                # Mapper para conversión entidad ↔ modelo
└── README.md                            # Documentación detallada
```

### 2. Servicios de Ejemplo
```
domain/services/
└── notification_service_with_entity.py  # Ejemplo de servicio usando entidades
```

### 3. Tests
```
tests/
└── test_notification_entity.py          # Tests unitarios completos (20 tests)
```

## Características Implementadas

### Entidad Notification (`domain/entities/notification.py`)

#### Atributos
- `notification_id`: ID único (opcional para nuevas notificaciones)
- `message`: Mensaje de la notificación (opcional)
- `notification_date`: Fecha y hora con timezone
- `invitation_id`: ID de la invitación relacionada
- `notification_type_id`: ID del tipo de notificación
- `notification_state_id`: ID del estado de la notificación
- `user_id`: ID del usuario destinatario
- `notification_type_name`: Nombre del tipo (opcional)
- `notification_state_name`: Nombre del estado (opcional)

#### Validaciones de Negocio
- Todos los IDs deben ser enteros positivos
- El mensaje no puede estar vacío si se proporciona
- Validación automática en `__post_init__`

#### Métodos de Negocio
- `create_new()`: Factory method para crear nuevas notificaciones
- `update_state()`: Actualizar estado con validación
- `is_pending()`, `is_sent()`, `is_read()`: Verificar estados
- `mark_as_sent()`, `mark_as_read()`: Cambiar a estados específicos
- `is_invitation_notification()`: Verificar si es notificación de invitación
- `get_formatted_date()`: Obtener fecha formateada
- `to_dict()`: Convertir a diccionario

### NotificationMapper (`domain/entities/notification_mapper.py`)

#### Métodos de Conversión
- `to_entity()`: Convierte modelo SQLAlchemy → entidad de dominio
- `to_model()`: Convierte entidad de dominio → modelo SQLAlchemy
- `update_model_from_entity()`: Actualiza modelo existente con datos de entidad

### Servicio de Ejemplo (`domain/services/notification_service_with_entity.py`)

#### Métodos Demostrativos
- `create_notification_entity()`: Crear entidad usando factory method
- `save_notification_entity()`: Persistir entidad en base de datos
- `get_user_notifications_as_entities()`: Obtener notificaciones como entidades
- `update_notification_state_with_entity()`: Actualizar estado usando entidad
- `send_notification_with_entity()`: Enviar notificación con lógica de entidad
- `process_notification_workflow()`: Workflow completo usando entidades

## Ventajas de la Implementación

### 1. Separación de Responsabilidades
- **Entidad**: Lógica de negocio pura
- **Mapper**: Conversión entre capas
- **Servicio**: Orquestación y casos de uso

### 2. Validación Automática
- Las reglas de negocio se validan automáticamente
- Errores claros y específicos
- Prevención de estados inválidos

### 3. Testabilidad
- 20 tests unitarios que cubren todos los casos
- Tests independientes de la base de datos
- Fácil mockeo para tests de integración

### 4. Mantenibilidad
- Lógica de negocio centralizada en la entidad
- Cambios en reglas de negocio en un solo lugar
- Código más expresivo y legible

### 5. Independencia de Framework
- No depende de SQLAlchemy u otros frameworks
- Puede usarse con cualquier sistema de persistencia
- Facilita migraciones futuras

## Ejemplos de Uso

### Crear Nueva Notificación
```python
from domain.entities import Notification

notification = Notification.create_new(
    message="Nueva invitación recibida",
    user_id=123,
    notification_type_id=1,
    invitation_id=456,
    notification_state_id=1
)
```

### Workflow Completo
```python
# Crear
notification = Notification.create_new(...)

# Validar reglas de negocio
if notification.is_invitation_notification():
    # Lógica específica para invitaciones
    pass

# Cambiar estado
notification.mark_as_sent()

# Persistir usando mapper
model = NotificationMapper.to_model(notification)
```

### Integración con Repositorio
```python
# Obtener de base de datos
models = repository.get_notifications_by_user_id(user_id)

# Convertir a entidades
entities = [NotificationMapper.to_entity(model) for model in models]

# Aplicar lógica de negocio
for entity in entities:
    if entity.is_pending():
        entity.mark_as_sent()
        # Actualizar en base de datos
```

## Configuración Requerida

### Estados de Notificación
Ajustar los IDs según tu base de datos:
- `1`: Pendiente (pending)
- `2`: Enviada (sent)  
- `3`: Leída (read)

### Tipos de Notificación
Configurar el método `is_invitation_notification()` según tus tipos específicos.

### Timezone
Por defecto usa "America/Bogota", configurable en `create_new()`.

## Próximos Pasos

1. **Integrar con el servicio existente**: Reemplazar gradualmente el uso directo de modelos SQLAlchemy
2. **Agregar más entidades**: Crear entidades para `NotificationState` y `NotificationType`
3. **Implementar Value Objects**: Para conceptos como `NotificationMessage` o `UserId`
4. **Agregar Domain Events**: Para notificar cambios de estado
5. **Crear Aggregates**: Si las notificaciones forman parte de agregados más grandes

## Tests Ejecutados

```bash
python -m pytest tests/test_notification_entity.py -v
```

**Resultado**: ✅ 20 tests pasaron exitosamente

La implementación está lista para usar y puede integrarse gradualmente con el código existente. 