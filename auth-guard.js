// ============================================================
// auth-guard.js — Gardien d'authentification Supabase
// VERTEXTRACK · Université Hassan 1er · Master TDTS 2025-2026
// ============================================================

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

// ── Identifiants Supabase ──────────────────────────────────
const SUPABASE_URL = 'https://kygrhqgyqqrylsxnshny.supabase.co';
const SUPABASE_KEY = 'sb_publishable_xEGDhI4c53TSQZOYrygUuA_4YTRjlNf';

// ── Client partagé (exporté pour les pages qui en ont besoin)
export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// ── Chemin vers la page de connexion ──────────────────────
const LOGIN_PAGE = 'login.html';

/**
 * Vérifie qu'une session active existe.
 * Si non connecté → redirige immédiatement vers login.html
 * @returns {Promise<import('@supabase/supabase-js').Session|null>}
 */
export async function checkSession() {
  const { data: { session }, error } = await supabase.auth.getSession();
  if (error || !session) {
    window.location.replace(LOGIN_PAGE);
    return null;
  }
  return session;
}

/**
 * Retourne l'utilisateur connecté, ou null si aucune session.
 * @returns {Promise<import('@supabase/supabase-js').User|null>}
 */
export async function getUser() {
  const { data: { session } } = await supabase.auth.getSession();
  return session ? session.user : null;
}

/**
 * Déconnecte l'utilisateur et redirige vers login.html
 */
export async function logout() {
  await supabase.auth.signOut();
  window.location.replace(LOGIN_PAGE);
}

/**
 * Injecte les infos utilisateur dans la navbar.
 * Cible l'élément #nav-user-area présent dans chaque page protégée.
 * @param {import('@supabase/supabase-js').Session} session
 */
export function injectNavUser(session) {
  const area = document.getElementById('nav-user-area');
  if (!area || !session) return;

  const email    = session.user.email || '';
  const initials = email.slice(0, 2).toUpperCase();

  area.innerHTML = `
    <span class="nav-user-badge" title="${email}">
      <span class="nav-user-avatar">${initials}</span>
      <span class="nav-user-email">${email}</span>
    </span>
    <button class="nav-btn-logout" id="btn-logout">Déconnexion</button>
  `;

  document.getElementById('btn-logout')
    .addEventListener('click', logout);
}
