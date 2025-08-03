import axios from "axios";


const BACKEND_FASTAPI_BASE = process.env.BACKEND_FASTAPI_BASE;

/**
 * Fetch tasks from the backend with optional filters.
 */
export async function fetchTasks(filters?: {
  assigned_to?: string;
  status?: string;
  project_id?: number;
  title?: string;
  due_date?: string; // YYYY-MM-DD
}) {
  console.log("fetchTasks called with filters:", filters);
  const safeFilters = filters || {};
  const params: Record<string, string | number> = {};

  if (safeFilters.assigned_to) params.assigned_to = safeFilters.assigned_to;
  if (safeFilters.status) params.status = safeFilters.status;
  if (safeFilters.project_id !== undefined)
    params.project_id = safeFilters.project_id;
  if (safeFilters.due_date) params.due_date = safeFilters.due_date;
   if (safeFilters.title) params.title = safeFilters.title;
  const { data } = await axios.get(`${BACKEND_FASTAPI_BASE}/tasks`, { params });
  return data || [];
}


/**
 * Fetch projects from the backend with optional filters.
 */
export async function fetchProjects(filters: {
  name?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
} = {}) {
   console.log("fetchProjects called with filters:", filters);
  const params: Record<string, string> = {};
  if (filters.name) params.name = filters.name;
  if (filters.status) params.status = filters.status;
  if (filters.start_date) params.start_date = filters.start_date;
  if (filters.end_date) params.end_date = filters.end_date;
  const { data } = await axios.get(`${BACKEND_FASTAPI_BASE}/projects`, { params });
  return data || [];
}


/**
 * Create a new project via the backend API.
 */
export async function createProject(project: {
  name: string;
  description?: string;
  start_date: string; // YYYY-MM-DD
  end_date?: string;  // YYYY-MM-DD
  status?: string;
}) {
  console.log("createProject called with:", project);
  try {
    const { data } = await axios.post(`${BACKEND_FASTAPI_BASE}/projects`, project);
    return data;
  } catch (err: any) {
    console.error("Error creating project:", err?.response?.data || err.message || err);
    throw err;
  }
}

/**
 * Create a new task via the backend API.
 */
export async function createTask(task: {
  title: string;
  assigned_to?: string;
  status?: string;
  due_date?: string;  // YYYY-MM-DD
  project_id: number;
}) {
  console.log("createTask called with:", task);
  try {
    const { data } = await axios.post(`${BACKEND_FASTAPI_BASE}/tasks`, task);
    return data;
  } catch (err: any) {
    console.error("Error creating task:", err?.response?.data || err.message || err);
    throw err;
  }
}
