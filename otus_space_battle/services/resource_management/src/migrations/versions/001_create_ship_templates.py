# create ship templates

Revision ID: 001
Revises: 
Create Date: 2024-03-17 00:00:00.000000
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Создаем enum для типов оружия
    weapon_type = postgresql.ENUM('torpedo', 'laser', 'missile', name='weapontype')
    weapon_type.create(op.get_bind())

    # Создаем таблицу шаблонов кораблей
    op.create_table(
        'ship_templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('in_use', sa.Boolean(), nullable=False, default=False),
        sa.Column('max_speed', sa.Float(), nullable=False),
        sa.Column('acceleration', sa.Float(), nullable=False),
        sa.Column('rotation_speed', sa.Float(), nullable=False),
        sa.Column('fuel_capacity', sa.Float(), nullable=False),
        sa.Column('fuel_consumption', sa.Float(), nullable=False),
        sa.Column('hull_strength', sa.Float(), nullable=False),
        sa.Column('shield_strength', sa.Float(), nullable=False),
        sa.Column('length', sa.Float(), nullable=False, default=10.0),
        sa.Column('width', sa.Float(), nullable=False, default=10.0),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Создаем таблицу оружия кораблей
    op.create_table(
        'ship_weapons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ship_template_id', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('torpedo', 'laser', 'missile', name='weapontype'), nullable=False),
        sa.Column('damage', sa.Float(), nullable=False),
        sa.Column('cooldown', sa.Float(), nullable=False),
        sa.Column('ammunition', sa.Integer(), nullable=False),
        sa.Column('range', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['ship_template_id'], ['ship_templates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Добавляем предустановленные шаблоны
    op.bulk_insert(
        sa.table(
            'ship_templates',
            sa.Column('id', sa.String()),
            sa.Column('name', sa.String()),
            sa.Column('description', sa.String()),
            sa.Column('is_default', sa.Boolean()),
            sa.Column('max_speed', sa.Float()),
            sa.Column('acceleration', sa.Float()),
            sa.Column('rotation_speed', sa.Float()),
            sa.Column('fuel_capacity', sa.Float()),
            sa.Column('fuel_consumption', sa.Float()),
            sa.Column('hull_strength', sa.Float()),
            sa.Column('shield_strength', sa.Float())
        ),
        [
            {
                'id': 'scout',
                'name': 'Разведчик',
                'description': 'Быстрый и маневренный корабль с минимальным вооружением',
                'is_default': True,
                'max_speed': 200.0,
                'acceleration': 50.0,
                'rotation_speed': 5.0,
                'fuel_capacity': 100.0,
                'fuel_consumption': 0.5,
                'hull_strength': 50.0,
                'shield_strength': 30.0
            },
            {
                'id': 'destroyer',
                'name': 'Эсминец',
                'description': 'Средний корабль с хорошим балансом характеристик',
                'is_default': True,
                'max_speed': 150.0,
                'acceleration': 30.0,
                'rotation_speed': 3.0,
                'fuel_capacity': 200.0,
                'fuel_consumption': 1.0,
                'hull_strength': 100.0,
                'shield_strength': 80.0
            },
            {
                'id': 'battleship',
                'name': 'Линкор',
                'description': 'Тяжелый корабль с мощным вооружением',
                'is_default': True,
                'max_speed': 100.0,
                'acceleration': 20.0,
                'rotation_speed': 2.0,
                'fuel_capacity': 300.0,
                'fuel_consumption': 2.0,
                'hull_strength': 200.0,
                'shield_strength': 150.0
            },
            {
                'id': 'carrier',
                'name': 'Носитель',
                'description': 'Большой корабль с множеством торпед',
                'is_default': True,
                'max_speed': 80.0,
                'acceleration': 15.0,
                'rotation_speed': 1.5,
                'fuel_capacity': 400.0,
                'fuel_consumption': 2.5,
                'hull_strength': 180.0,
                'shield_strength': 120.0
            },
            {
                'id': 'interceptor',
                'name': 'Перехватчик',
                'description': 'Сверхбыстрый корабль для атак и отступлений',
                'is_default': True,
                'max_speed': 250.0,
                'acceleration': 60.0,
                'rotation_speed': 6.0,
                'fuel_capacity': 80.0,
                'fuel_consumption': 1.0,
                'hull_strength': 40.0,
                'shield_strength': 20.0
            }
        ]
    )

    # Добавляем оружие для предустановленных шаблонов
    op.bulk_insert(
        sa.table(
            'ship_weapons',
            sa.Column('ship_template_id', sa.String()),
            sa.Column('type', sa.Enum('torpedo', 'laser', 'missile', name='weapontype')),
            sa.Column('damage', sa.Float()),
            sa.Column('cooldown', sa.Float()),
            sa.Column('ammunition', sa.Integer()),
            sa.Column('range', sa.Float())
        ),
        [
            # Разведчик
            {
                'ship_template_id': 'scout',
                'type': 'laser',
                'damage': 10.0,
                'cooldown': 1.0,
                'ammunition': -1,
                'range': 300.0
            },
            # Эсминец
            {
                'ship_template_id': 'destroyer',
                'type': 'torpedo',
                'damage': 50.0,
                'cooldown': 3.0,
                'ammunition': 20,
                'range': 500.0
            },
            {
                'ship_template_id': 'destroyer',
                'type': 'laser',
                'damage': 15.0,
                'cooldown': 1.5,
                'ammunition': -1,
                'range': 400.0
            },
            # Линкор
            {
                'ship_template_id': 'battleship',
                'type': 'missile',
                'damage': 100.0,
                'cooldown': 5.0,
                'ammunition': 10,
                'range': 800.0
            },
            {
                'ship_template_id': 'battleship',
                'type': 'torpedo',
                'damage': 70.0,
                'cooldown': 4.0,
                'ammunition': 15,
                'range': 600.0
            },
            # Носитель
            {
                'ship_template_id': 'carrier',
                'type': 'torpedo',
                'damage': 40.0,
                'cooldown': 2.0,
                'ammunition': 50,
                'range': 450.0
            },
            # Перехватчик
            {
                'ship_template_id': 'interceptor',
                'type': 'laser',
                'damage': 20.0,
                'cooldown': 0.5,
                'ammunition': -1,
                'range': 200.0
            },
            {
                'ship_template_id': 'interceptor',
                'type': 'missile',
                'damage': 60.0,
                'cooldown': 4.0,
                'ammunition': 5,
                'range': 400.0
            }
        ]
    )

def downgrade():
    op.drop_table('ship_weapons')
    op.drop_table('ship_templates')
    weapon_type = postgresql.ENUM('torpedo', 'laser', 'missile', name='weapontype')
    weapon_type.drop(op.get_bind()) 