"""add_task_profile_time_spent_timestamps

Revision ID: af4114c4863b
Revises: 0c583446766d
Create Date: 2025-06-16 15:52:46.950079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'af4114c4863b'
down_revision: Union[str, None] = '0c583446766d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define TaskProfile enum type for use in this migration
task_profile_enum = postgresql.ENUM('DEVELOPMENT', 'ANALYTICS', 'DOCUMENTATION', 'GENERAL', name='taskprofile')

def upgrade() -> None:
    # Create the ENUM type in the database
    task_profile_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns to 'tasks' table
    op.add_column('tasks', sa.Column('task_profile', task_profile_enum, nullable=False, server_default='GENERAL'))
    op.add_column('tasks', sa.Column('time_spent', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('tasks', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('tasks', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)) # Using onupdate for client-side updates, server_default for creation.

    # Make existing columns non-nullable if they aren't already. Assuming they might be nullable based on typical initial setups.
    # If previous migrations already made them non-nullable, these might be redundant but harmless.
    op.alter_column('tasks', 'title', existing_type=sa.String(length=100), nullable=False)
    op.alter_column('tasks', 'status', existing_type=postgresql.ENUM('PLANNED', 'IN_PROGRESS', 'COMPLETED', name='taskstatus'), nullable=False, existing_server_default=sa.text("'PLANNED'::taskstatus"))
    op.alter_column('tasks', 'author_id', existing_type=sa.Integer(), nullable=False)

    # Drop old columns from 'tasks' table
    # Check if 'date' and 'task_type' columns exist before dropping, to be safe with existing data states
    # For simplicity in this context, we'll assume they exist as per the model changes implies.
    # In a real scenario, you might inspect table first or handle potential errors.
    # op.drop_column('tasks', 'date', if_exists=True) # `if_exists` is not a standard op.drop_column param. Need to remove or handle differently.
                                                 # For now, assuming it exists based on previous schema dump.
    # op.drop_column('tasks', 'task_type', if_exists=True) # Same as above.
    # Removing the if_exists=True as it is not supported
    bind = op.get_bind()
    insp = sa.inspect(bind)
    columns = [col['name'] for col in insp.get_columns('tasks')]
    if 'date' in columns:
        op.drop_column('tasks', 'date')
    if 'task_type' in columns:
        op.drop_column('tasks', 'task_type')


    # Modify 'task_user_association' table
    # Make columns non-nullable
    op.alter_column('task_user_association', 'task_id', existing_type=sa.Integer(), nullable=False)
    op.alter_column('task_user_association', 'user_id', existing_type=sa.Integer(), nullable=False)
    # Add composite primary key
    # Ensure no existing PK before adding. If one exists (e.g. an auto-created rowid), this might need adjustment.
    # Dropping existing PK if it's just a single column default one might be needed.
    # For now, assuming no conflicting PK.
    op.create_primary_key(
        'pk_task_user_association',
        'task_user_association',
        ['task_id', 'user_id']
    )

def downgrade() -> None:
    # Drop primary key from 'task_user_association'
    op.drop_constraint('pk_task_user_association', 'task_user_association', type_='primary')
    # Make columns nullable again
    op.alter_column('task_user_association', 'task_id', existing_type=sa.Integer(), nullable=True)
    op.alter_column('task_user_association', 'user_id', existing_type=sa.Integer(), nullable=True)

    # Add back old columns to 'tasks' table
    op.add_column('tasks', sa.Column('task_type', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('tasks', sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))

    # Make columns nullable again or revert to previous state for 'tasks'
    op.alter_column('tasks', 'title', existing_type=sa.String(length=100), nullable=True)
    # When downgrading status, ensure the ENUM 'taskstatus' is still defined.
    op.alter_column('tasks', 'status', existing_type=postgresql.ENUM('PLANNED', 'IN_PROGRESS', 'COMPLETED', name='taskstatus'), nullable=True, existing_server_default=sa.text("'PLANNED'::taskstatus"))
    op.alter_column('tasks', 'author_id', existing_type=sa.Integer(), nullable=True)

    # Drop new columns from 'tasks' table
    op.drop_column('tasks', 'updated_at')
    op.drop_column('tasks', 'created_at')
    op.drop_column('tasks', 'time_spent')
    op.drop_column('tasks', 'task_profile')

    # Drop the ENUM type from the database
    task_profile_enum.drop(op.get_bind(), checkfirst=True)
