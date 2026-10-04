PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    metodo TEXT NOT NULL,

    score_zona REAL NOT NULL,
    score_carga REAL NOT NULL,
    score_total REAL NOT NULL,

    carga_antes INTEGER NOT NULL,
    carga_despues INTEGER NOT NULL,
    capacidad_antes REAL NOT NULL,
    capacidad_despues REAL NOT NULL,
    utilizacion_antes REAL NOT NULL,

    coincidencia_zona INTEGER NOT NULL
        CHECK (coincidencia_zona IN (0, 1)),
    fallback_geografico INTEGER NOT NULL
        CHECK (fallback_geografico IN (0, 1)),
    estado_geografico TEXT NOT NULL,
    explicacion_zona TEXT NOT NULL,
    razon TEXT NOT NULL,

    ejecutado_en TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_assignments_record_id
    ON assignments(record_id);

CREATE INDEX IF NOT EXISTS idx_assignments_usuario_id
    ON assignments(usuario_id);

CREATE INDEX IF NOT EXISTS idx_assignments_ejecutado_en
    ON assignments(ejecutado_en);


CREATE TABLE IF NOT EXISTS assignment_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    assignment_id INTEGER NOT NULL UNIQUE
        REFERENCES assignments(id),

    record_id INTEGER NOT NULL,
    metodo TEXT NOT NULL,
    parametros TEXT NOT NULL,
    usuario_seleccionado_id INTEGER NOT NULL,

    criterio_seleccion TEXT NOT NULL,
    criterio_desempate TEXT,

    candidatos_json TEXT NOT NULL,

    estado_geografico TEXT NOT NULL,
    coincidencia_zona INTEGER NOT NULL
        CHECK (coincidencia_zona IN (0, 1)),
    fallback_geografico INTEGER NOT NULL
        CHECK (fallback_geografico IN (0, 1)),
    explicacion_zona TEXT NOT NULL,
    razon TEXT NOT NULL,

    ejecutado_por TEXT NOT NULL,
    ejecutado_en TEXT NOT NULL,

    reemplaza_assignment_id INTEGER
        REFERENCES assignments(id),

    prompt TEXT,
    respuesta_modelo TEXT
);

CREATE INDEX IF NOT EXISTS idx_assignment_traces_record_id
    ON assignment_traces(record_id);

CREATE INDEX IF NOT EXISTS idx_assignment_traces_ejecutado_en
    ON assignment_traces(ejecutado_en);


CREATE TABLE IF NOT EXISTS active_assignments (
    record_id INTEGER PRIMARY KEY,

    assignment_id INTEGER NOT NULL UNIQUE
        REFERENCES assignments(id),

    usuario_id INTEGER NOT NULL,

    assigned_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY,
    estado TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_active_assignments_usuario_id
    ON active_assignments(usuario_id);