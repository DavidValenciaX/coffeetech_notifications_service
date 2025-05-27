# Entidades del Dominio - Notification

## Descripción

La entidad `Notification` representa una notificación en la capa de dominio del sistema. Esta entidad encapsula la lógica de negocio y las reglas relacionadas con las notificaciones, proporcionando una interfaz limpia y consistente para trabajar con notificaciones independientemente de la implementación de persistencia.

## Estructura de Archivos

```
domain/entities/
├── __init__.py                 # Exporta las entidades principales
├── notification.py             # Entidad Notification
├── notification_mapper.py      # Mapper para conversión entre entidad y modelo
└── README.md                   # Esta documentación
```

## Características de la Entidad Notification

### Atributos Principales

- `notification_id`: ID único de la notificación (opcional para nuevas notificaciones)
- `message`: Mensaje de la notificación (opcional)
- `notification_date`: Fecha y hora de la notificación
- `invitation_id`: ID de la invitación relacionada
- `notification_type_id`: ID del tipo de notificación
- `notification_state_id`: ID del estado de la notificación
- `user_id`: ID del usuario que recibe la notificación
- `notification_type_name`: Nombre del tipo de notificación (opcional)
- `notification_state_name`: Nombre del estado de la notificación (opcional)

### Validaciones de Negocio

La entidad incluye validaciones automáticas que se ejecutan al crear o modificar una notificación:

- `user_id` debe ser un entero positivo
- `invitation_id` debe ser un entero positivo
- `notification_type_id` debe ser un entero positivo
- `notification_state_id` debe ser un entero positivo
- `message` no puede estar vacío si se proporciona

## Uso de la Entidad

### 1. Crear una Nueva Notificación

```python
from domain.entities import Notification

# Método recomendado: usar el factory method
notification = Notification.create_new(
    message="Nueva invitación recibida",
    user_id=123,
    notification_type_id=1,
    invitation_id=456,
    notification_state_id=1  # Pendiente
)

# Método alternativo: constructor directo
from datetime import datetime
import pytz

notification = Notification(
    notification_id=None,
    message="Nueva invitación recibida",
    notification_date=datetime.now(pytz.timezone("America/Bogota")),
    invitation_id=456,
    notification_type_id=1,
    notification_state_id=1,
    user_id=123
)
```

### 2. Trabajar con Estados de Notificación

```python
# Verificar estados
if notification.is_pending():
    print("La notificación está pendiente")

if notification.is_sent():
    print("La notificación ha sido enviada")

if notification.is_read():
    print("La notificación ha sido leída")

# Cambiar estados
notification.mark_as_sent()
notification.mark_as_read()

# Cambio de estado personalizado
notification.update_state(new_state_id=3)
```

### 3. Validaciones y Reglas de Negocio

```python
# Verificar tipo de notificación
if notification.is_invitation_notification():
    print("Es una notificación de invitación")

# Obtener fecha formateada
formatted_date = notification.get_formatted_date("%d/%m/%Y %H:%M")
print(f"Fecha: {formatted_date}")

# Convertir a diccionario
notification_dict = notification.to_dict()
```

### 4. Usar el Mapper para Persistencia

```python
from domain.entities import NotificationMapper
from models.models import Notifications

# Convertir entidad a modelo SQLAlchemy
notification_entity = Notification.create_new(...)
notification_model = NotificationMapper.to_model(notification_entity)

# Convertir modelo SQLAlchemy a entidad
db_notification = session.query(Notifications).first()
notification_entity = NotificationMapper.to_entity(db_notification)

# Actualizar modelo existente con datos de entidad
NotificationMapper.update_model_from_entity(existing_model, updated_entity)
```

## Integración con Servicios

### Ejemplo de Servicio usando Entidades

```python
from domain.entities import Notification, NotificationMapper
from domain.repositories.notification_repository import NotificationRepositoryInterface

class NotificationService:
    def __init__(self, repository: NotificationRepositoryInterface):
        self.repository = repository
    
    def create_notification(self, message: str, user_id: int, 
                          notification_type_id: int, invitation_id: int) -> Notification:
        # Crear entidad
        notification = Notification.create_new(
            message=message,
            user_id=user_id,
            notification_type_id=notification_type_id,
            invitation_id=invitation_id,
            notification_state_id=1  # Pendiente
        )
        
        # Guardar en base de datos
        saved_model = self.repository.create_notification(
            message=notification.message,
            user_id=notification.user_id,
            notification_type_id=notification.notification_type_id,
            invitation_id=notification.invitation_id,
            notification_state_id=notification.notification_state_id
        )
        
        # Retornar entidad actualizada
        return NotificationMapper.to_entity(saved_model)
    
    def process_notification_workflow(self, notification: Notification) -> Notification:
        # Aplicar lógica de negocio
        if notification.is_invitation_notification():
            # Lógica específica para invitaciones
            pass
        
        # Marcar como enviada
        notification.mark_as_sent()
        
        # Actualizar en base de datos
        updated_model = self.repository.update_notification_state(
            notification.notification_id,
            notification.notification_state_id
        )
        
        return NotificationMapper.to_entity(updated_model)
```

## Ventajas de Usar Entidades

1. **Encapsulación**: La lógica de negocio está contenida en la entidad
2. **Validación**: Las reglas de negocio se validan automáticamente
3. **Testabilidad**: Fácil de testear sin dependencias externas
4. **Mantenibilidad**: Cambios en la lógica de negocio centralizados
5. **Independencia**: No depende de frameworks de persistencia
6. **Expresividad**: El código es más legible y expresivo

## Estados de Notificación Predefinidos

La entidad asume los siguientes IDs de estado (ajustar según tu base de datos):

- `1`: Pendiente (pending)
- `2`: Enviada (sent)
- `3`: Leída (read)

## Consideraciones

1. **IDs de Estado**: Ajusta los métodos `is_pending()`, `is_sent()`, `is_read()`, `mark_as_sent()`, y `mark_as_read()` según los IDs reales en tu base de datos.

2. **Tipos de Notificación**: El método `is_invitation_notification()` debe ajustarse según tu implementación específica.

3. **Timezone**: Por defecto usa "America/Bogota", pero puede configurarse.

4. **Validaciones**: Puedes agregar más validaciones de negocio en el método `_validate()`.

## Ejemplo Completo

Ver el archivo `domain/services/notification_service_with_entity.py` para un ejemplo completo de cómo integrar la entidad con el servicio existente. 