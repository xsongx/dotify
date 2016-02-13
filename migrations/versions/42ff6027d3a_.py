"""empty message

Revision ID: 42ff6027d3a
Revises: 1b134bc80cc
Create Date: 2016-02-13 10:08:56.323842

"""

# revision identifiers, used by Alembic.
revision = '42ff6027d3a'
down_revision = '1b134bc80cc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'country_vectors', 'countries', ['country_id'], ['id'])
    op.create_foreign_key(None, 'song_vectors', 'songs', ['song_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'song_vectors', type_='foreignkey')
    op.drop_constraint(None, 'country_vectors', type_='foreignkey')
    ### end Alembic commands ###
