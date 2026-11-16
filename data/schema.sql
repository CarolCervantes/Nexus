-- NEXUS Relational Database Schema
-- Version: 1.0.0
-- Database Engine: SQLite 3

PRAGMA foreign_keys = ON;

-- 1. PROYECTOS
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    category TEXT NOT NULL CHECK(category IN ('personal', 'académico', 'profesional', 'otro')) DEFAULT 'personal',
    status TEXT NOT NULL CHECK(status IN ('activo', 'pausado', 'completado', 'cancelado')) DEFAULT 'activo',
    priority TEXT NOT NULL CHECK(priority IN ('P1', 'P2', 'P3', 'P4')) DEFAULT 'P3',
    target_date TEXT, -- Formato YYYY-MM-DD
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 2. TAREAS
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT NOT NULL CHECK(priority IN ('P1', 'P2', 'P3', 'P4')) DEFAULT 'P3',
    status TEXT NOT NULL CHECK(status IN ('pendiente', 'en_progreso', 'completada', 'cancelada')) DEFAULT 'pendiente',
    due_date TEXT, -- Formato YYYY-MM-DD
    due_time TEXT, -- Formato HH:MM (opcional)
    estimated_minutes INTEGER DEFAULT 30,
    completed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 3. COMPROMISOS (Entregables / Acuerdos con terceros)
CREATE TABLE IF NOT EXISTS commitments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    counterparty TEXT NOT NULL, -- Persona, cliente, profesor, equipo
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT NOT NULL, -- Formato YYYY-MM-DD
    status TEXT NOT NULL CHECK(status IN ('pendiente', 'cumplido', 'renegociado', 'cancelado')) DEFAULT 'pendiente',
    importance TEXT NOT NULL CHECK(importance IN ('critica', 'alta', 'media', 'baja')) DEFAULT 'alta',
    related_project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 4. NOTAS Y CONOCIMIENTO
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('idea', 'nota', 'recurso', 'referencia')) DEFAULT 'nota',
    tags TEXT, -- Separados por comas: ej. 'ia,investigacion,ideas'
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 5. BITÁCORA HISTÓRICA DE DECISIONES
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    context TEXT NOT NULL,
    decision_made TEXT NOT NULL,
    rationale TEXT,
    impact TEXT,
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL
);

-- 6. SESIONES Y CONTINUIDAD
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_start TEXT NOT NULL,
    session_end TEXT,
    summary_actions TEXT,
    items_updated INTEGER DEFAULT 0
);

-- 7. AUDITORÍA Y TRAZABILIDAD
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action_type TEXT NOT NULL, -- INSERT, UPDATE, DELETE, BACKUP, RESTORE, SYNC
    entity_type TEXT NOT NULL, -- task, project, commitment, note, decision, system
    entity_id INTEGER,
    details TEXT
);

-- ÍNDICES PARA BÚSQUEDA Y RENDIMIENTO RÁPIDO
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_category ON projects(category);

CREATE INDEX IF NOT EXISTS idx_commitments_due_date ON commitments(due_date);
CREATE INDEX IF NOT EXISTS idx_commitments_status ON commitments(status);

CREATE INDEX IF NOT EXISTS idx_notes_category ON notes(category);
CREATE INDEX IF NOT EXISTS idx_decisions_created_at ON decisions(created_at);
