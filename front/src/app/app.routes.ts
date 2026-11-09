import { Routes } from '@angular/router';
import { ConsultaPublica } from './pages/consulta-publica/consulta-publica';
import { Selos } from './pages/selos/selos';
import { Inicio } from './pages/inicio/inicio';

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
];