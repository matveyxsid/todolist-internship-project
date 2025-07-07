import React, { useEffect, useState } from 'react';
import {
  Configuration,
  DefaultApi,
  TodoOut,
  CreateTodoTodosPostRequest,
  UpdateCompletedStatusTodosTodoIdPatchRequest,
  DeleteTodoTodosTodoIdDeleteRequest,
} from './api/client';

const config = new Configuration({
  basePath: process.env.REACT_APP_API_BASE_URL,
});
const api = new DefaultApi(config);

const frontendVersion = process.env.REACT_APP_VERSION;

function App() {
  const [todos, setTodos] = useState<TodoOut[]>([]);
  const [newTitle, setNewTitle] = useState('');

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = () => {
    api.getTodosTodosGet().then((response) => {
      setTodos(response);
    });
  };

  const handleAddTodo = () => {
    if (!newTitle.trim()) return;

    const payload: CreateTodoTodosPostRequest = {
      todoCreate: {
        title: newTitle,
        completed: false,
      },
    };

    api.createTodoTodosPost(payload).then((newTodo) => {
      setTodos((prev) => [...prev, newTodo]);
      setNewTitle('');
    });
  };

  const handleDelete = (id: number) => {
    const payload: DeleteTodoTodosTodoIdDeleteRequest = {
      todoId: id,
    };

    api.deleteTodoTodosTodoIdDelete(payload).then(() => {
      setTodos((prev) => prev.filter((todo) => todo.id !== id));
    });
  };

  const toggleCompleted = (todo: TodoOut) => {
    const payload: UpdateCompletedStatusTodosTodoIdPatchRequest = {
      todoId: todo.id!,
      bodyUpdateCompletedStatusTodosTodoIdPatch: {
        completed: !todo.completed,
      },
    };

    api.updateCompletedStatusTodosTodoIdPatch(payload).then((updatedTodo) => {
      setTodos((prev) =>
        prev.map((t) => (t.id === updatedTodo.id ? updatedTodo : t))
      );
    });
  };

  return (
    <div style={{
      backgroundColor: '#121212',
      minHeight: '100vh',
      color: '#f0f0f0',
      fontFamily: 'Arial, sans-serif',
      padding: '2rem',
    }}>
      <h1 style={{ textAlign: 'center', color: '#00ffcc' }}>To-Do List</h1>

      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
        <input
          type="text"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="New task..."
          style={{
            padding: '0.5rem',
            fontSize: '1rem',
            width: '300px',
            marginRight: '1rem',
            borderRadius: '4px',
            border: '1px solid #333',
            backgroundColor: '#222',
            color: '#fff'
          }}
        />
        <button
          onClick={handleAddTodo}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '1rem',
            borderRadius: '4px',
            border: 'none',
            backgroundColor: '#00ffcc',
            color: '#000',
            cursor: 'pointer'
          }}
        >
          +
        </button>
      </div>

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {todos.map((todo) => (
          <li key={todo.id} style={{
            backgroundColor: '#1e1e1e',
            padding: '1rem',
            borderRadius: '8px',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div
              onClick={() => toggleCompleted(todo)}
              style={{
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              <span style={{
                fontSize: '1.5rem'
              }}>
                {todo.completed ? '✅' : '⏳'}
              </span>
              <span style={{
                textDecoration: todo.completed ? 'line-through' : 'none'
              }}>
                {todo.title}
              </span>
            </div>

            <button
              onClick={() => handleDelete(todo.id!)}
              style={{
                backgroundColor: '#ff4d4d',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                padding: '0.3rem 0.6rem',
                cursor: 'pointer'
              }}
            >
              🗑 Delete
            </button>
          </li>
        ))}
      </ul>
      <p style={{ textAlign: 'center', marginTop: '2rem', fontSize: '0.9rem', color: '#888' }}>
        Frontend version: v{frontendVersion}
      </p>
    </div>
  );
}



export default App;
