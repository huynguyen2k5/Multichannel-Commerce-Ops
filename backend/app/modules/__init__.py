"""MCO Modular Monolith bounded contexts.

Each submodule defines an explicit public facade (__all__) exporting public services,
schemas, models, and router endpoints. Repositories are private module-internal
persistence adapters and MUST NOT be exported through the public module facade.
"""
