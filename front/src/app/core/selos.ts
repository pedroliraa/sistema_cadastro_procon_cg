const IMAGEM_SELO: Record<string, string> = {
  'Excelência': '/assets/selo_excelencia.png',
  'Referência': '/assets/selo_referencia.png',
  'Confiável': '/assets/selo_confiavel.png',
  'Qualificado': '/assets/selo_qualificado.png',
};

export function imagemDoSelo(nome: string | null | undefined): string | null {
  return nome ? (IMAGEM_SELO[nome] ?? null) : null;
}
