# -*- coding: utf-8 -*-
"""Steps communs Behave."""
from behave import given

@given('l\'application est démarrée avec une base vide')
def step_app_started(context):
    """L'app est déjà prête via environment (client créé)."""
    pass
