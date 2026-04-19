// ============================================================
// auth-guard.js — Gardien d'authentification + Rôles RBAC
// VERTEXTRACK · Université Hassan 1er · Master TDTS 2025-2026
// ============================================================

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

// ── Identifiants Supabase ──────────────────────────────────
const SUPABASE_URL = 'https://kygrhqgyqqrylsxnshny.supabase.co';
const SUPABASE_KEY = 'sb_publishable_xEGDhI4c53TSQZOYrygUuA_4YTRjlNf';

// ── Client partagé ─────────────────────────────────────────
export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// ── Constantes ─────────────────────────────────────────────
const LOGIN_PAGE     = 'login.html';
const ROLE_CACHE_KEY = 'vt_user_role'; // clé sessionStorage pour le cache

// ── Couleurs et libellés par rôle ──────────────────────────
export const ROLE_LABELS = { admin: 'Admin', coach: 'Coach', medical: 'Médical' };
export const ROLE_COLORS = { admin: '#00b4d8', coach: '#22c55e', medical: '#f59e0b' };

// ===========================================================
// checkSession()
// Vérifie qu'une session active existe.
// Si non connecté → redirige vers login.html
// ===========================================================
export async function checkSession() {
  const { data: { session }, error } = await supabase.auth.getSession();
  if (error || !session) {
    window.location.replace(LOGIN_PAGE);
    return null;
  }
  return session;
}

// ===========================================================
// getUser()
// Retourne l'utilisateur connecté, ou null.
// ===========================================================
export async function getUser() {
  const { data: { session } } = await supabase.auth.getSession();
  return session ? session.user : null;
}

// ===========================================================
// logout()
// Vide le cache du rôle, déconnecte et redirige.
// ===========================================================
export async function logout() {
  sessionStorage.removeItem(ROLE_CACHE_KEY); // vider le cache rôle
  await supabase.auth.signOut();
  window.location.replace(LOGIN_PAGE);
}

// ===========================================================
// getRole()
// Récupère le rôle de l'utilisateur depuis Supabase.
// Utilise sessionStorage pour éviter une requête à chaque page.
// Si aucun rôle trouvé → déconnexion automatique + message.
// @returns {Promise<'admin'|'coach'|'medical'|null>}
// ===========================================================
export async function getRole() {
  // 1. Lire le cache (évite une requête Supabase à chaque navigation)
  const cached = sessionStorage.getItem(ROLE_CACHE_KEY);
  if (cached) return cached;

  // 2. Vérifier qu'une session est active
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) return null;

  // 3. Requête sur la table user_roles
  const { data, error } = await supabase
    .from('user_roles')
    .select('role')
    .eq('user_id', session.user.id)
    .single();

  if (error || !data?.role) {
    // Rôle non trouvé → déconnexion forcée avec message d'erreur
    console.warn('[VERTEXTRACK] Rôle utilisateur introuvable — déconnexion.');
    sessionStorage.setItem(
      'vt_login_error',
      "Votre compte n'a pas de rôle assigné. Contactez l'administrateur."
    );
    await logout();
    return null;
  }

  // 4. Mettre en cache pour la durée de la session de navigation
  sessionStorage.setItem(ROLE_CACHE_KEY, data.role);
  return data.role;
}

// ===========================================================
// injectNavUser(session, role)
// Injecte avatar + email + badge rôle + bouton déconnexion
// dans l'élément #nav-user-area de chaque page protégée.
// @param {Session} session
// @param {'admin'|'coach'|'medical'|null} role
// ===========================================================
export function injectNavUser(session, role = null) {
  const area = document.getElementById('nav-user-area');
  if (!area || !session) return;

  const email    = session.user.email || '';
  const initials = email.slice(0, 2).toUpperCase();
  const color    = role ? (ROLE_COLORS[role] || '#00c8ff') : '#00c8ff';
  const label    = role ? (ROLE_LABELS[role] || role)      : '';

  // Badge rôle (visible uniquement si rôle défini)
  const roleBadge = role ? `
    <span class="nav-role-badge" style="
      background:${color}1a;
      color:${color};
      border:1px solid ${color}40;
    ">${label}</span>` : '';

  area.innerHTML = `
    <span class="nav-user-badge" title="${email} — ${label}">
      <span class="nav-user-avatar" style="
        background:linear-gradient(135deg,${color},#007fa8);
      ">${initials}</span>
      <span class="nav-user-email">${email}</span>
      ${roleBadge}
    </span>
    <button class="nav-btn-logout" id="btn-logout">Déconnexion</button>
  `;

  document.getElementById('btn-logout').addEventListener('click', logout);
}

// ===========================================================
// applyRBAC(role)
// Applique les restrictions d'accès selon le rôle :
//   - Masque les éléments [data-role] non autorisés
//   - Masque les colonnes .col-medical pour les coaches
// @param {'admin'|'coach'|'medical'} role
// ===========================================================
export function applyRBAC(role) {
  if (!role) return;

  // 1. Masquer les blocs [data-role] interdits
  document.querySelectorAll('[data-role]').forEach(el => {
    const allowed = el.dataset.role.split(',').map(r => r.trim());
    if (!allowed.includes(role)) {
      el.style.display = 'none';
    }
  });

  // 2. Pour le rôle COACH : masquer les colonnes médicales du tableau
  if (role === 'coach') {
    document.querySelectorAll('.col-medical').forEach(el => {
      el.style.display = 'none';
    });
    // Réajuster la grille du tableau (2fr 1fr 80px au lieu de 2fr 1fr 1fr 1fr 1fr 80px)
    document.querySelectorAll('.table-header, .table-row').forEach(el => {
      el.style.gridTemplateColumns = '2fr 1fr 80px';
    });
    // Réajuster la grille des KPI (2 colonnes au lieu de 4)
    const kpiRow = document.querySelector('.kpi-row');
    if (kpiRow) kpiRow.style.gridTemplateColumns = 'repeat(2,1fr)';
  }
}
