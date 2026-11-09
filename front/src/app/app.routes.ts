import { Routes } from '@angular/router';
import { ConsultaPublica } from './pages/consulta-publica/consulta-publica';
import { Selos } from './pages/selos/selos';

export const routes: Routes = [
  {
    path: 'consulta-publica',
    component: ConsultaPublica,
  },
  {
    path: 'selos',
    component: Selos,
  },
  {
    path: '',
    redirectTo: 'consulta-publica',
    pathMatch: 'full',
  },
];