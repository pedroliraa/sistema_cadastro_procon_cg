// Remove tudo que não é letra/número e limita a 14 caracteres
export function limparCnpj(valor: string | null | undefined): string {
  return (valor ?? '').toUpperCase().replace(/[^0-9A-Z]/g, '').slice(0, 14);
}

// 12345678000195 → 12.345.678/0001-95
export function formatarCnpj(valor: string | null | undefined): string {
  const v = limparCnpj(valor);
  const partes = [v.slice(0, 2), v.slice(2, 5), v.slice(5, 8), v.slice(8, 12), v.slice(12, 14)];

  let resultado = partes[0];
  if (partes[1]) resultado += '.' + partes[1];
  if (partes[2]) resultado += '.' + partes[2];
  if (partes[3]) resultado += '/' + partes[3];
  if (partes[4]) resultado += '-' + partes[4];
  return resultado;
}

export function limparTelefone(valor: string | null | undefined): string {
  return (valor ?? '').replace(/\D/g, '').slice(0, 11);
}

// 83999998888 → (83) 99999-8888 | 8333334444 → (83) 3333-4444
export function formatarTelefone(valor: string | null | undefined): string {
  const d = limparTelefone(valor);
  if (!d) return '';
  if (d.length <= 2) return `(${d}`;
  if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
  if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
  return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}
