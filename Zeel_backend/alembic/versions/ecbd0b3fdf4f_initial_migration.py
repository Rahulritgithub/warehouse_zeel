"""Initial migration

Revision ID: ecbd0b3fdf4f
Revises: 
Create Date: 2025-12-04 12:22:02.999925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = 'ecbd0b3fdf4f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop tables in correct dependency order (child tables first)
    # Using raw SQL to avoid the cascade parameter issue
    
    # Get connection
    connection = op.get_bind()
    
    # Drop all tables with CASCADE using raw SQL
    tables = [
        'transactions',
        'request_items',
        'items',
        'requests',
        'storage_bins',
        'users',
        'racks'
    ]
    
    for table in tables:
        connection.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
    
    # Drop indexes if they still exist (though CASCADE should handle them)
    # But let's be safe and drop them explicitly
    try:
        op.drop_index('ix_storage_bins_id', table_name='storage_bins', if_exists=True)
        op.drop_index('ix_storage_bins_rfid', table_name='storage_bins', if_exists=True)
    except:
        pass
    
    try:
        op.drop_index('ix_requests_id', table_name='requests', if_exists=True)
    except:
        pass
        
    try:
        op.drop_index('ix_items_id', table_name='items', if_exists=True)
        op.drop_index('ix_items_rfid', table_name='items', if_exists=True)
    except:
        pass
    
    try:
        op.drop_index('ix_request_items_id', table_name='request_items', if_exists=True)
    except:
        pass
        
    try:
        op.drop_index('ix_racks_id', table_name='racks', if_exists=True)
    except:
        pass
    
    try:
        op.drop_index('ix_users_id', table_name='users', if_exists=True)
    except:
        pass
    
    try:
        op.drop_index('ix_transactions_id', table_name='transactions', if_exists=True)
    except:
        pass


def downgrade() -> None:
    """Downgrade schema."""
    # Create tables in correct dependency order (parent tables first)
    op.create_table('racks',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('racks_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('rack_id', sa.VARCHAR(length=255), nullable=True),
    sa.Column('location', sa.VARCHAR(length=255), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id', name='racks_pkey'),
    sa.UniqueConstraint('rack_id', name='racks_rack_id_key')
    )
    op.create_index(op.f('ix_racks_id'), 'racks', ['id'], unique=False)
    
    op.create_table('storage_bins',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('rfid', sa.VARCHAR(length=100), nullable=True),
    sa.Column('rack_id', sa.VARCHAR(length=100), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['rack_id'], ['racks.rack_id'], name=op.f('storage_bins_rack_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('storage_bins_pkey'))
    )
    op.create_index(op.f('ix_storage_bins_rfid'), 'storage_bins', ['rfid'], unique=True)
    op.create_index(op.f('ix_storage_bins_id'), 'storage_bins', ['id'], unique=False)
    
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(), nullable=True),
    sa.Column('password', sa.VARCHAR(), nullable=True),
    sa.Column('role', sa.VARCHAR(), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('users_pkey')),
    sa.UniqueConstraint('username', name=op.f('users_username_key'))
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    op.create_table('requests',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('req_from', sa.VARCHAR(length=255), nullable=True),
    sa.Column('req_to', sa.VARCHAR(length=255), nullable=True),
    sa.Column('description', sa.VARCHAR(length=500), nullable=True),
    sa.Column('created_date', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('request_date', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('requests_pkey'))
    )
    op.create_index(op.f('ix_requests_id'), 'requests', ['id'], unique=False)
    
    op.create_table('items',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('rfid', sa.VARCHAR(length=100), nullable=True),
    sa.Column('rack_id', sa.VARCHAR(length=100), nullable=True),
    sa.Column('storage_bin_id', sa.INTEGER(), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['rack_id'], ['racks.rack_id'], name=op.f('items_rack_id_fkey')),
    sa.ForeignKeyConstraint(['storage_bin_id'], ['storage_bins.id'], name=op.f('items_storage_bin_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('items_pkey'))
    )
    op.create_index(op.f('ix_items_rfid'), 'items', ['rfid'], unique=True)
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    
    op.create_table('request_items',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('request_id', sa.INTEGER(), nullable=True),
    sa.Column('item_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], name=op.f('request_items_item_id_fkey')),
    sa.ForeignKeyConstraint(['request_id'], ['requests.id'], name=op.f('request_items_request_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('request_items_pkey'))
    )
    op.create_index(op.f('ix_request_items_id'), 'request_items', ['id'], unique=False)
    
    op.create_table('transactions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('type', postgresql.ENUM('INWARD', 'OUTWARD', 'RETURN', name='transactiontype'), nullable=False),
    sa.Column('reason', sa.VARCHAR(length=255), nullable=True),
    sa.Column('item_id', sa.INTEGER(), nullable=True),
    sa.Column('transaction_date', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], name=op.f('transactions_item_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('transactions_pkey'))
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)