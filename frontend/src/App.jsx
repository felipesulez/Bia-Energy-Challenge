import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [view, setView] = useState("dashboard");
  const [assignments, setAssignments] = useState([]);
  const [preview, setPreview] = useState(null);
  const [selectedAssignment, setSelectedAssignment] = useState(null);

  const [evaluationDate, setEvaluationDate] = useState("2026-10-04");
  const [executedBy, setExecutedBy] = useState("felipe");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [showReassignForm, setShowReassignForm] = useState(false);

  useEffect(() => {
    loadAssignments();
  }, []);

  async function loadAssignments() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/assignments`);

      if (!response.ok) {
        throw new Error("No fue posible obtener las asignaciones.");
      }

      const data = await response.json();
      setAssignments(data.assignments ?? []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadAssignmentDetail(assignmentId) {
    try {
      setLoading(true);
      setError("");
      setMessage("");

      const response = await fetch(
        `${API_URL}/assignments/${assignmentId}`
      );

      if (!response.ok) {
        throw new Error("No fue posible obtener el detalle.");
      }

      const data = await response.json();

      setSelectedAssignment(data);
      setShowReassignForm(false);
      setView("detail");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function runPreview() {
    try {
      setLoading(true);
      setError("");
      setMessage("");
      setPreview(null);

      const response = await fetch(`${API_URL}/assignments/preview`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          evaluation_date: evaluationDate,
        }),
      });

      if (!response.ok) {
        throw new Error("No fue posible generar el preview.");
      }

      const data = await response.json();
      setPreview(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function executeAssignments() {
    try {
      setLoading(true);
      setError("");
      setMessage("");

      const response = await fetch(`${API_URL}/assignments/execute`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          evaluation_date: evaluationDate,
          executed_by: executedBy,
        }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);

        throw new Error(
          data?.detail ?? "No fue posible ejecutar las asignaciones."
        );
      }

      const data = await response.json();

      setMessage(
        `Asignación ejecutada correctamente. ${
          data.assignments?.length ?? 0
        } registros procesados.`
      );

      await loadAssignments();
      setView("history");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function reassignAssignment() {
    if (!selectedAssignment) {
      return;
    }

    try {
      setLoading(true);
      setError("");
      setMessage("");

      const response = await fetch(
        `${API_URL}/assignments/${selectedAssignment.assignment_id}/reassign`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            evaluation_date: evaluationDate,
            executed_by: executedBy,
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json().catch(() => null);

        throw new Error(
          data?.detail ?? "No fue posible realizar la reasignación."
        );
      }

      const data = await response.json();

      setSelectedAssignment(data);
      setShowReassignForm(false);

      setMessage(
        `Reasignación completada. La nueva asignación activa es #${data.assignment_id}.`
      );

      await loadAssignments();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const activeAssignments = assignments.filter(
    (assignment) => assignment.es_activa
  );

  const reassignedAssignments = assignments.filter(
    (assignment) => assignment.reemplaza_assignment_id !== null
  );

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <span className="eyebrow">Motor de Asignación Comercial</span>
          <h1>Panel de asignaciones</h1>
        </div>

        <button className="refresh-button" onClick={loadAssignments}>
          Actualizar
        </button>
      </header>

      <nav className="navigation">
        <button
          className={view === "dashboard" ? "nav-button active" : "nav-button"}
          onClick={() => {
            setView("dashboard");
            setError("");
            setMessage("");
          }}
        >
          Dashboard
        </button>

        <button
          className={view === "preview" ? "nav-button active" : "nav-button"}
          onClick={() => {
            setView("preview");
            setError("");
            setMessage("");
          }}
        >
          Preview
        </button>

        <button
          className={view === "history" ? "nav-button active" : "nav-button"}
          onClick={() => {
            setView("history");
            setError("");
            setMessage("");
          }}
        >
          Historial
        </button>
      </nav>

      <main className="content">
        {error && <div className="error">{error}</div>}
        {message && <div className="success">{message}</div>}

        {view === "dashboard" && (
          <>
            <section className="metrics">
              <article className="metric-card">
                <span>Asignaciones totales</span>
                <strong>{assignments.length}</strong>
              </article>

              <article className="metric-card">
                <span>Asignaciones activas</span>
                <strong>{activeAssignments.length}</strong>
              </article>

              <article className="metric-card">
                <span>Reasignaciones</span>
                <strong>{reassignedAssignments.length}</strong>
              </article>
            </section>

            <section className="panel">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">Trazabilidad</span>
                  <h2>Últimas asignaciones</h2>
                </div>

                <span className="count">
                  {assignments.length} registros
                </span>
              </div>

              {loading ? (
                <div className="empty-state">
                  Cargando asignaciones...
                </div>
              ) : (
                <AssignmentTable
                  assignments={assignments}
                  onSelect={loadAssignmentDetail}
                />
              )}
            </section>
          </>
        )}

        {view === "preview" && (
          <section className="panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">Motor de asignación</span>
                <h2>Previsualizar asignaciones</h2>
              </div>
            </div>

            <div className="form-grid">
              <label>
                Fecha de evaluación
                <input
                  type="date"
                  value={evaluationDate}
                  onChange={(event) =>
                    setEvaluationDate(event.target.value)
                  }
                />
              </label>

              <label>
                Método
                <input value="weighted_rules" disabled />
              </label>

              <label>
                Ejecutado por
                <input
                  value={executedBy}
                  onChange={(event) =>
                    setExecutedBy(event.target.value)
                  }
                />
              </label>
            </div>

            <div className="actions">
              <button
                className="primary-button"
                onClick={runPreview}
                disabled={loading}
              >
                {loading ? "Procesando..." : "Previsualizar"}
              </button>

              {preview && (
                <button
                  className="secondary-button"
                  onClick={executeAssignments}
                  disabled={loading}
                >
                  Ejecutar asignación
                </button>
              )}
            </div>

            {preview && (
              <div className="preview-result">
                <div className="preview-summary">
                  <div>
                    <span>Registros</span>
                    <strong>
                      {preview.assignments?.length ?? 0}
                    </strong>
                  </div>

                  <div>
                    <span>Fecha</span>
                    <strong>{evaluationDate}</strong>
                  </div>

                  <div>
                    <span>Persistencia</span>
                    <strong>No</strong>
                  </div>
                </div>

                <AssignmentTable
                  assignments={preview.assignments ?? []}
                  onSelect={null}
                  previewMode
                />
              </div>
            )}
          </section>
        )}

        {view === "history" && (
          <section className="panel">
            <div className="panel-header">
              <div>
                <span className="eyebrow">Auditoría</span>
                <h2>Historial de asignaciones</h2>
              </div>

              <span className="count">
                {assignments.length} registros
              </span>
            </div>

            <AssignmentTable
              assignments={assignments}
              onSelect={loadAssignmentDetail}
              showAll
            />
          </section>
        )}

        {view === "detail" && selectedAssignment && (
          <section className="detail-grid">
            <div className="panel">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">Explicabilidad</span>
                  <h2>
                    Asignación #{selectedAssignment.assignment_id}
                  </h2>
                </div>

                <span
                  className={
                    selectedAssignment.es_activa
                      ? "status active"
                      : "status inactive"
                  }
                >
                  {selectedAssignment.es_activa
                    ? "Activa"
                    : "Histórica"}
                </span>
              </div>

              <div className="detail-content">
                <DetailRow
                  label="Registro"
                  value={selectedAssignment.record_id}
                />

                <DetailRow
                  label="Usuario asignado"
                  value={selectedAssignment.usuario_id}
                />

                <DetailRow
                  label="Método"
                  value={selectedAssignment.metodo}
                />

                <DetailRow
                  label="Puntuación total"
                  value={selectedAssignment.score_total?.toFixed(2)}
                />

                <DetailRow
                  label="Score zona"
                  value={selectedAssignment.score_zona?.toFixed(2)}
                />

                <DetailRow
                  label="Score carga"
                  value={selectedAssignment.score_carga?.toFixed(2)}
                />

                <DetailRow
                  label="Estado geográfico"
                  value={selectedAssignment.estado_geografico}
                />

                <DetailRow
                  label="Carga antes"
                  value={selectedAssignment.carga_antes}
                />

                <DetailRow
                  label="Carga después"
                  value={selectedAssignment.carga_despues}
                />
              </div>
            </div>

            <div className="panel explanation-panel">
              <div className="panel-header">
                <div>
                  <span className="eyebrow">¿Por qué?</span>
                  <h2>Explicación de la decisión</h2>
                </div>
              </div>

              <div className="explanation">
                <p>{selectedAssignment.razon}</p>
              </div>

              {selectedAssignment.reemplaza_assignment_id && (
                <div className="trace-box">
                  <span>Reemplaza asignación</span>
                  <strong>
                    #{selectedAssignment.reemplaza_assignment_id}
                  </strong>
                </div>
              )}

              {selectedAssignment.es_activa && !showReassignForm && (
                <button
                  className="primary-button detail-action"
                  onClick={() => setShowReassignForm(true)}
                >
                  Reasignar asignación
                </button>
              )}

              {showReassignForm && (
                <div className="reassign-form">
                  <div>
                    <span className="eyebrow">Nueva evaluación</span>
                    <h3>Confirmar reasignación</h3>
                  </div>

                  <label>
                    Fecha de evaluación
                    <input
                      type="date"
                      value={evaluationDate}
                      onChange={(event) =>
                        setEvaluationDate(event.target.value)
                      }
                    />
                  </label>

                  <label>
                    Ejecutado por
                    <input
                      value={executedBy}
                      onChange={(event) =>
                        setExecutedBy(event.target.value)
                      }
                    />
                  </label>

                  <div className="reassign-actions">
                    <button
                      className="secondary-button"
                      onClick={() => setShowReassignForm(false)}
                      disabled={loading}
                    >
                      Cancelar
                    </button>

                    <button
                      className="primary-button"
                      onClick={reassignAssignment}
                      disabled={loading}
                    >
                      {loading
                        ? "Reasignando..."
                        : "Confirmar reasignación"}
                    </button>
                  </div>
                </div>
              )}

              <button
                className="secondary-button back-button"
                onClick={() => {
                  setShowReassignForm(false);
                  setView("history");
                }}
              >
                Volver al historial
              </button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function DetailRow({ label, value }) {
  return (
    <div className="detail-row">
      <span>{label}</span>
      <strong>{value ?? "—"}</strong>
    </div>
  );
}

function AssignmentTable({
  assignments,
  onSelect,
  showAll = false,
  previewMode = false,
}) {
  const visibleAssignments = showAll
    ? assignments
    : assignments.slice().reverse().slice(0, 10);

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Registro</th>
            <th>Usuario</th>
            <th>Método</th>
            <th>Puntuación</th>
            <th>Zona</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          {visibleAssignments.map((assignment, index) => (
            <tr key={assignment.assignment_id ?? `preview-${index}`}>
              <td>
                {previewMode
                  ? "—"
                  : `#${assignment.assignment_id}`}
              </td>

              <td>{assignment.record_id}</td>

              <td>{assignment.usuario_id}</td>

              <td>
                <span className="method">
                  {assignment.metodo}
                </span>
              </td>

              <td>
                <strong>
                  {assignment.score_total?.toFixed(2)}
                </strong>
              </td>

              <td>
                {assignment.estado_geografico ?? "—"}
              </td>

              <td>
                {previewMode ? (
                  <span className="status preview">
                    Propuesta
                  </span>
                ) : (
                  <span
                    className={
                      assignment.es_activa
                        ? "status active"
                        : "status inactive"
                    }
                  >
                    {assignment.es_activa
                      ? "Activa"
                      : "Histórica"}
                  </span>
                )}
              </td>

              <td>
                {onSelect && (
                  <button
                    className="link-button"
                    onClick={() =>
                      onSelect(assignment.assignment_id)
                    }
                  >
                    Ver detalle
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;