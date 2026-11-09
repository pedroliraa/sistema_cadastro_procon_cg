import { Routes } from '@angular/router';
import { ConsultaPublica } from './pages/consulta-publica/consulta-publica';
import { Selos } from './pages/selos/selos';
import { Inicio } from './pages/inicio/inicio';
import { Login } from './pages/login/login';
import { AdminEmpresas } from './pages/admin-empresas/admin-empresas';
import { AdminEmpresaDetalhe } from './pages/admin-empresa-detalhe/admin-empresa-detalhe';
import { authGuard } from './core/auth.guard';
import { AdminEmpresaFormulario } from './pages/admin-empresa-formulario/admin-empresa-formulario';

export const routes: Routes = [
  {
    path: '',
    component: Inicio,
    pathMatch: 'full',
  },
  {
    path: 'consulta-publica',
    component: ConsultaPublica,
  },
  {
    path: 'selos',
    component: Selos,
  },
  {
    path: 'login',
    component: Login,
  },
  // Área restrita (precisa de login)
  {
    path: 'admin',
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'empresas', pathMatch: 'full' },
      { path: 'empresas', component: AdminEmpresas },
      { path: 'empresas/nova', component: AdminEmpresaFormulario },
      { path: 'empresas/:id/editar', component: AdminEmpresaFormulario },
      { path: 'empresas/:id', component: AdminEmpresaDetalhe },
      
      
    ],
  },
];
