# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 be-cloud.be
#                       Jerome Sonnet <jerome.sonnet@be-cloud.be>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import api, fields, models, tools, _
from openerp.exceptions import MissingError

_logger = logging.getLogger(__name__)

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx

class SaturnXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, saturn):
        saturn.ensure_one()
        sheet = workbook.add_worksheet('main')
        
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        
        i = 0
        sheet.write(i, 0, u'Code Fase de l’Ecole supérieure des Arts')
        sheet.write(i, 1, u'Année académique en cours (= année N)')
        sheet.write(i, 2, u'Type d’études')
        sheet.write(i, 3, u'Domaine d’études')
        sheet.write(i, 4, u'Cycle d’études et durée du cycle')
        sheet.write(i, 5, u'Section d’études (Musique) ou AESS (tous les domaines)')
        sheet.write(i, 6, u'Option')
        sheet.write(i, 7, u'Année d’études dans le cycle')
        sheet.write(i, 8, u'Inscriptions multiples')
        sheet.write(i, 9, u'Jeunes Talents (Musique)')
        sheet.write(i, 10, u'Finalité du 2e cycle')
        sheet.write(i, 11, u'Spécialité (Musique)')
        sheet.write(i, 12, u'Nom de l’étudiant')
        sheet.write(i, 13, u'Premier prénom de l’étudiant')
        sheet.write(i, 14, u'Initiales des autres prénoms')
        sheet.write(i, 15, u'Numéro matricule')
        sheet.write(i, 16, u'Sexe')
        sheet.write(i, 17, u'Nationalité')
        sheet.write(i, 18, u'Lieu de naissance')
        sheet.write(i, 19, u'Pays du lieu de naissance')
        sheet.write(i, 20, u'Date de naissance de l’étudiant')
        sheet.write(i, 21, u'Domicile légal en Belgique')
        sheet.write(i, 22, u'Domicile légal à l’étranger')
        sheet.write(i, 23, u'Numéro de Registre national')
        sheet.write(i, 24, u'Régulier / Libre')
        sheet.write(i, 25, u'Date d’abandon')
        sheet.write(i, 26, u'Ancien/Nouveau')
        sheet.write(i, 27, u'Etalement')
        sheet.write(i, 28, u'Mobilité')
        sheet.write(i, 29, u'Première génération')
        sheet.write(i, 30, u'Type de mobilité')
        sheet.write(i, 31, u'Nationalité de l’étudiant au regard du financement')
        sheet.write(i, 32, u'Modalité de l’inscription au regard du financement')
        sheet.write(i, 33, u'Etudiant boursier')
        sheet.write(i, 34, u'Minerval')
        sheet.write(i, 35, u'Date de réception du paiement du minerval')
        sheet.write(i, 36, u'Droit d’inscription spécifique (DIS)')
        sheet.write(i, 37, u'Date de réception du paiement du droit d’inscription spécifique')
        sheet.write(i, 38, u'Etudiant de condition modeste')
        sheet.write(i, 39, u'Titre d’accès à la première année du cycle court ou du premier cycle du type long')
        sheet.write(i, 40, u'Année de délivrance du titre d’accès à la 1re année d’études')
        sheet.write(i, 41, u'Type de secondaire obligatoire suivi')
        sheet.write(i, 42, u'Etablissement d’enseignement de la FWB ou de la DG où le titre d’accès a été obtenu')
        sheet.write(i, 43, u'Pays dans lequel le titre d’accès équivalent a été obtenu')
        sheet.write(i, 44, u'Titre d’accès aux autres années que la première année des études de type court ou long')
        sheet.write(i, 45, u'Diplôme obtenu dans l’enseignement supérieur')
        sheet.write(i, 46, u'Année d’obtention du diplôme en F2')
        sheet.write(i, 47, u'Autre diplôme obtenu dans l’enseignement supérieur (1)')
        sheet.write(i, 48, u'Année d’obtention du diplôme en F4')
        sheet.write(i, 49, u'Pays dans lequel le diplôme indiqué à la variable F2 a été obtenu')
        sheet.write(i, 50, u'Activité principale au cours de l’année académique n‐1')
        sheet.write(i, 51, u'Etablissement d’enseignement de la FWB concerné par G2')
        sheet.write(i, 52, u'Domaine d’études concerné par G2')
        sheet.write(i, 53, u'Année d’études se rapportant à G2')
        sheet.write(i, 54, u'Résultats se rapportant à G2')
        sheet.write(i, 55, u'Activité principale au cours de l’année académique n‐2')
        sheet.write(i, 56, u'Etablissement d’enseignement de la FWB concerné par G7')
        sheet.write(i, 57, u'Domaine d’études concerné par G7')
        sheet.write(i, 58, u'Année d’études se rapportant G7')
        sheet.write(i, 59, u'Résultats se rapportant à G7')
        sheet.write(i, 60, u'Activité principale au cours de l’année académique n‐3')
        sheet.write(i, 61, u'Etablissement d’enseignement de la FWB concerné par G12')
        sheet.write(i, 62, u'Domaine d’études concerné par G12')
        sheet.write(i, 63, u'Année d’études se rapportant à G12')
        sheet.write(i, 64, u'Résultats se rapportant à G12')
        sheet.write(i, 65, u'Activité principale au cours de l’année académique n‐4')
        sheet.write(i, 66, u'Etablissement d’enseignement de la FWB concerné par G17')
        sheet.write(i, 67, u'Domaine d’études concerné par G17')
        sheet.write(i, 68, u'Année d’études se rapportant à G17')
        sheet.write(i, 69, u'Résultats se rapportant à G17')
        sheet.write(i, 70, u'Activité principale au cours de l’année académique n‐5')
        sheet.write(i, 71, u'Etablissement d’enseignement de la FWB concerné par G22')
        sheet.write(i, 72, u'Domaine d’études concerné par G22')
        sheet.write(i, 73, u'Année d’études se rapportant à G22')
        sheet.write(i, 74, u'Résultats se rapportant à G22')
        sheet.write(i, 75, u'Pays de l’activité académique se rapportant à G2')
        sheet.write(i, 76, u'Résultats de la 1re session (juillet 2013)')
        sheet.write(i, 77, u'Résultats de la 2e session (septembre 2013)')
        sheet.write(i, 78, u'Résultats de session prolongée')
        sheet.write(i, 79, u'Date du diplôme') 
        i = 1
        for bloc_id in saturn.bloc_ids:
            sheet.write(i, 0, bloc_id.field_a1 or '')
            sheet.write(i, 1, bloc_id.field_a2.name or '')
            if bloc_id.field_a3:
                sheet.write(i, 2, bloc_id.field_a3[0].upper())
            sheet.write(i, 3, bloc_id.field_a4.saturn_code or '')
            sheet.write(i, 4, bloc_id.field_a5.saturn_code or '')
            sheet.write(i, 5, bloc_id.field_a6.saturn_code or '')
            sheet.write(i, 6, bloc_id.field_a7.saturn_code or '')
            sheet.write(i, 7, bloc_id.field_a8 or '')
            sheet.write(i, 8, bloc_id.field_a9 or '')
            sheet.write(i, 9, bloc_id.field_a10)
            sheet.write(i, 10, bloc_id.field_a11 or '')
            sheet.write(i, 11, bloc_id.field_a12.saturn_code or '')
            sheet.write(i, 12, bloc_id.field_b1 or '')
            sheet.write(i, 13, bloc_id.field_b2 or '')
            sheet.write(i, 14, bloc_id.field_b3 or '')
            sheet.write(i, 15, bloc_id.field_b4 or '')
            if bloc_id.field_b5:
                sheet.write(i, 16, bloc_id.field_b5[0].upper())
            sheet.write(i, 17, bloc_id.field_b6.name or '')
            sheet.write(i, 18, bloc_id.field_b7 or '')
            sheet.write(i, 19, bloc_id.field_b8.name or '')
            if bloc_id.field_b9:
                sheet.write_datetime(i, 20, fields.Date.from_string(bloc_id.field_b9), date_format)
            sheet.write(i, 21, bloc_id.field_b10 or '')
            sheet.write(i, 22, bloc_id.field_b11 or '')
            sheet.write(i, 23, bloc_id.field_b12 or '')
            sheet.write(i, 24, bloc_id.field_c1 or '')
            sheet.write(i, 25, bloc_id.field_c2 or '')
            sheet.write(i, 26, bloc_id.field_c3 or '')
            sheet.write(i, 27, bloc_id.field_c4 or '')
            sheet.write(i, 28, bloc_id.field_c5 or '')
            sheet.write(i, 29, bloc_id.field_c14 or '')
            sheet.write(i, 30, bloc_id.field_c19 or '')
            sheet.write(i, 31, bloc_id.field_d1 or '')
            sheet.write(i, 32, bloc_id.field_d2 or '')
            sheet.write(i, 33, bloc_id.field_d3 or '')
            sheet.write(i, 34, bloc_id.field_d4 or '')
            sheet.write(i, 35, bloc_id.field_d5 or '')
            sheet.write(i, 36, bloc_id.field_d6 or '')
            sheet.write(i, 37, bloc_id.field_d7 or '')
            sheet.write(i, 38, bloc_id.field_d8 or '')
            sheet.write(i, 39, bloc_id.field_e1 or '')
            sheet.write(i, 40, bloc_id.field_e2.name or '')
            sheet.write(i, 41, bloc_id.field_e3 or '')
            sheet.write(i, 42, bloc_id.field_e4.code_fase or '')
            sheet.write(i, 43, bloc_id.field_e5.name or '')
            sheet.write(i, 44, bloc_id.field_f1 or '')
            sheet.write(i, 45, bloc_id.field_f2 or '')
            sheet.write(i, 46, bloc_id.field_f3.name or '')
            sheet.write(i, 47, bloc_id.field_f4 or '')
            sheet.write(i, 48, bloc_id.field_f5.name or '')
            sheet.write(i, 49, bloc_id.field_f10.name or '')
            sheet.write(i, 50, bloc_id.field_g2 or '')
            sheet.write(i, 51, bloc_id.field_g3.code_fase or '')
            sheet.write(i, 52, bloc_id.field_g4.code or '')
            sheet.write(i, 53, bloc_id.field_g5 or '')
            sheet.write(i, 54, bloc_id.field_g6 or '')
            sheet.write(i, 55, bloc_id.field_g7 or '')
            sheet.write(i, 56, bloc_id.field_g8.code_fase or '')
            sheet.write(i, 57, bloc_id.field_g9.code or '')
            sheet.write(i, 58, bloc_id.field_g10 or '')
            sheet.write(i, 59, bloc_id.field_g11 or '')
            sheet.write(i, 60, bloc_id.field_g12 or '')
            sheet.write(i, 61, bloc_id.field_g13.code_fase or '')
            sheet.write(i, 62, bloc_id.field_g14.code or '')
            sheet.write(i, 63, bloc_id.field_g15 or '')
            sheet.write(i, 64, bloc_id.field_g16 or '')
            sheet.write(i, 65, bloc_id.field_g17 or '')
            sheet.write(i, 66, bloc_id.field_g18.code_fase or '')
            sheet.write(i, 67, bloc_id.field_g19.code or '')
            sheet.write(i, 68, bloc_id.field_g20 or '')
            sheet.write(i, 69, bloc_id.field_g21 or '')
            sheet.write(i, 70, bloc_id.field_g22 or '')
            sheet.write(i, 71, bloc_id.field_g23.code_fase or '')
            sheet.write(i, 72, bloc_id.field_g24.code or '')
            sheet.write(i, 73, bloc_id.field_g25 or '')
            sheet.write(i, 74, bloc_id.field_g26 or '')
            sheet.write(i, 75, bloc_id.field_g27.name or '')
            sheet.write(i, 76, bloc_id.field_h1 or '')
            sheet.write(i, 77, bloc_id.field_h2 or '')
            sheet.write(i, 78, bloc_id.field_h3 or '')
            if bloc_id.field_h4:
                sheet.write_datetime(i, 79, fields.Date.from_string(bloc_id.field_h4), date_format)
            i = i + 1

SaturnXlsx('report.school.saturn.xlsx','school.saturn')

class Annexe5Xlsx(ReportXlsx):

    def _is_dcc_bloc(self, bloc_id):
        older_bloc_credits = bloc_id.program_id.historical_bloc_1_credits + bloc_id.program_id.historical_bloc_2_credits + sum(bloc_id.program_id.bloc_ids.filtered(lambda b : b.year_id.name <= bloc_id.year_id.name).mapped('total_acquiered_credits'))
        return older_bloc_credits >= bloc_id.program_id.required_credits

    def generate_xlsx_report(self, workbook, data, saturn):
        saturn.ensure_one()
        sheet = workbook.add_worksheet('main')
        
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        
        i = 0
        sheet.write(i, 0, u'Catégorie HE/Domaine ESA')
        sheet.write(i, 1, u'GRADE ACADEMIQUE')
        sheet.write(i, 2, u'OPTION/FINALITE/ORIENTATION')
        sheet.write(i, 3, u'DOMAINE')
        sheet.write(i, 4, u'INSCRIPTION 16-17')
        sheet.write(i, 5, u'TYPE')
        sheet.write(i, 6, u'NOM')
        sheet.write(i, 7, u'PRENOM')
        sheet.write(i, 8, u'SEXE')
        sheet.write(i, 9, u'LIEU DE NAISSANCE')
        sheet.write(i, 10, u'jour naiss')
        sheet.write(i, 11, u'mois naiss')
        sheet.write(i, 12, u'annee naiss')
        sheet.write(i, 13, u'nationalité')
        sheet.write(i, 14, u'numéro nationnal')
        sheet.write(i, 15, u'minerval')
        sheet.write(i, 16, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 17, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 18, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 19, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 20, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 21, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 22, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 23, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 24, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 25, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 26, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 27, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 28, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 29, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 30, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 31, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 32, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 33, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 34, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 35, u'Activité')
        sheet.write(i, 36, u'Inscr.')
        sheet.write(i, 37, u'Code saturn')
        sheet.write(i, 38, u'U/HE/ESA/PS')
        sheet.write(i, 39, u'Résultat')
        sheet.write(i, 40, u'PAE_num')
        sheet.write(i, 41, u'PAE_dén.')
        sheet.write(i, 42, u'Activité')
        sheet.write(i, 43, u'Inscr.')
        sheet.write(i, 44, u'Code saturn')
        sheet.write(i, 45, u'U/HE/ESA/PS')
        sheet.write(i, 46, u'Résultat')
        sheet.write(i, 47, u'PAE_num')
        sheet.write(i, 48, u'PAE_dén.')
        sheet.write(i, 49, u'Activité')
        sheet.write(i, 50, u'Inscr.')
        sheet.write(i, 51, u'Code saturn')
        sheet.write(i, 52, u'U/HE/ESA/PS')
        sheet.write(i, 53, u'Résultat')
        sheet.write(i, 54, u'PAE_num')
        sheet.write(i, 55, u'PAE_dén.')
        sheet.write(i, 56, u'Activité')
        sheet.write(i, 57, u'Inscr.')
        sheet.write(i, 58, u'Code saturn')
        sheet.write(i, 59, u'U/HE/ESA/PS')
        sheet.write(i, 60, u'Résultat')
        sheet.write(i, 61, u'PAE_num')
        sheet.write(i, 62, u'PAE_dén.')
        sheet.write(i, 63, u'Activité')
        sheet.write(i, 64, u'Inscr.')
        sheet.write(i, 65, u'Code saturn')
        sheet.write(i, 66, u'U/HE/ESA/PS')
        sheet.write(i, 67, u'Résultat')
        sheet.write(i, 68, u'PAE_num')
        sheet.write(i, 69, u'PAE_dén.')
        sheet.write(i, 70, u'date inscription')
        sheet.write(i, 71, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 72, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 73, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 74, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 75, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 76, u'REGULIER')
        sheet.write(i, 77, u'IRREGULIER')
        sheet.write(i, 78, u'FINANCABLE')
        sheet.write(i, 79, u'NON FINANCABLE')
        sheet.write(i, 80, u'PAE 16-17')
        sheet.write(i, 81, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 82, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 83, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 84, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 85, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 86, u'A ENCODER SUR FICHIER SEPARE')
        sheet.write(i, 87, u'PAE id')
        sheet.write(i, 88, u'Student id')
        sheet.write(i, 89, u'Cycle id')
        i = 1
        
        # years for history
        year_minus_1 = saturn.year_id.previous if saturn.year_id else False
        year_minus_2 = year_minus_1.previous if year_minus_1 else False
        year_minus_3 = year_minus_2.previous if year_minus_2 else False
        year_minus_4 = year_minus_3.previous if year_minus_3 else False
        year_minus_5 = year_minus_4.previous if year_minus_4 else False
        
        for bloc_id in saturn.bloc_ids:
            sheet.write(i, 0, u'ESA')
            sheet.write(i, 1, bloc_id.field_a5.short_name or '')
            _logger.info(bloc_id.name)
            if bloc_id.source_bloc_section_id and bloc_id.source_bloc_track_id and bloc_id.source_bloc_speciality_id :
                sheet.write(i, 2, bloc_id.source_bloc_section_id.name or '' + '/' + bloc_id.source_bloc_track_id.name or '' + '/' + bloc_id.source_bloc_speciality_id.name or '')
            sheet.write(i, 3, bloc_id.field_a4.name or '')
            #sheet.write(i, 4, u'INSCRIPTION 16-17')
            #sheet.write(i, 5, u'TYPE')
            sheet.write(i, 6, bloc_id.field_b1)
            sheet.write(i, 7, bloc_id.field_b2)
            if bloc_id.field_b5:
                sheet.write(i, 8, bloc_id.field_b5[0].upper())
            sheet.write(i, 9, bloc_id.field_b7 or '')
            #sheet.write(i, 10, u'jour naiss')
            #sheet.write(i, 11, u'mois naiss')
            #sheet.write(i, 12, u'annee naiss')
            sheet.write(i, 13, bloc_id.field_b6.name or '')
            sheet.write(i, 14, bloc_id.field_b12 or '')
            sheet.write(i, 15, u'minerval')
            #sheet.write(i, 27, u'A ENCODER SUR FICHIER SEPARE')
            #sheet.write(i, 28, u'A ENCODER SUR FICHIER SEPARE')
            #sheet.write(i, 29, u'A ENCODER SUR FICHIER SEPARE')
            #sheet.write(i, 30, u'A ENCODER SUR FICHIER SEPARE')
            #sheet.write(i, 31, u'A ENCODER SUR FICHIER SEPARE')
            #sheet.write(i, 32, u'A ENCODER SUR FICHIER SEPARE')
            #sheet.write(i, 33, u'A ENCODER SUR FICHIER SEPARE')
            #sheet.write(i, 34, u'A ENCODER SUR FICHIER SEPARE')
            year_id = year_minus_5
            program_id = bloc_id.program_id
            hist_bloc_id = program_id.bloc_ids.filtered(lambda b: b.year_id == year_id)
            if not hist_bloc_id:
                # Try to find a bloc in another cycle for the given year
                hist_bloc_id = self.env['school.individual_bloc'].search([('student_id','=',bloc_id.student_id.id),('year_id','=',year_id.id)])
            if hist_bloc_id :
                hist_bloc_id = hist_bloc_id[0]
                sheet.write(i, 35, 'ETU')
                if self._is_dcc_bloc(hist_bloc_id) :
                    sheet.write(i, 36, 'DCC')
                elif hist_bloc_id.source_bloc_level == '1' :
                    sheet.write(i, 36, '1A1C')
                elif hist_bloc_id.source_bloc_level in ('2','3') :
                    sheet.write(i, 36, '>45')
                else:
                    sheet.write(i, 36, '1A2C')
                sheet.write(i, 37, program_id.track_id.saturn_code)
                sheet.write(i, 38, 'ESA')
                if hist_bloc_id.state in ('awarded_first_session','awarded_second_session'):
                    sheet.write(i, 39, 'R')
                else :
                    sheet.write(i, 39, 'E')
                sheet.write(i, 40, hist_bloc_id.total_acquiered_credits)
                sheet.write(i, 41, hist_bloc_id.total_credits)
            else :    
                hist_id = self.env['school.student_annexe5_entry'].search([('year_id','=',year_id.id),('student_id','=',bloc_id.student_id.id)])
                if hist_id:
                    sheet.write(i, 35, hist_id.activite or '')
                    sheet.write(i, 36, hist_id.inscription or '')
                    sheet.write(i, 37, hist_id.code_saturn or '')
                    sheet.write(i, 38, hist_id.type or '')
                    sheet.write(i, 39, hist_id.resultat or '')
                    sheet.write(i, 40, hist_id.pae_num or '')
                    sheet.write(i, 41, hist_id.pae_den or '')
            year_id = year_minus_4
            hist_bloc_id = program_id.bloc_ids.filtered(lambda b: b.year_id == year_id)
            if not hist_bloc_id:
                # Try to find a bloc in another cycle for the given year
                hist_bloc_id = self.env['school.individual_bloc'].search([('student_id','=',bloc_id.student_id.id),('year_id','=',year_id.id)])
            if hist_bloc_id :
                hist_bloc_id = hist_bloc_id[0]
                sheet.write(i, 42, 'ETU')
                if self._is_dcc_bloc(hist_bloc_id) :
                    sheet.write(i, 43, 'DCC')
                elif hist_bloc_id.source_bloc_level == '1' :
                    sheet.write(i, 43, '1A1C')
                elif hist_bloc_id.source_bloc_level in ('2','3') :
                    sheet.write(i, 43, '>45')
                else:
                    sheet.write(i, 43, '1A2C')
                sheet.write(i, 44, program_id.track_id.saturn_code)
                sheet.write(i, 45, 'ESA')
                if hist_bloc_id.state in ('awarded_first_session','awarded_second_session'):
                    sheet.write(i, 46, 'R')
                else :
                    sheet.write(i, 46, 'E')
                sheet.write(i, 47, hist_bloc_id.total_acquiered_credits)
                sheet.write(i, 48, hist_bloc_id.total_credits)
            else :    
                hist_id = self.env['school.student_annexe5_entry'].search([('year_id','=',year_id.id),('student_id','=',bloc_id.student_id.id)])
                if hist_id:
                    sheet.write(i, 42, hist_id.activite or '')
                    sheet.write(i, 43, hist_id.inscription or '')
                    sheet.write(i, 44, hist_id.code_saturn or '')
                    sheet.write(i, 45, hist_id.type or '')
                    sheet.write(i, 46, hist_id.resultat or '')
                    sheet.write(i, 47, hist_id.pae_num or '')
                    sheet.write(i, 48, hist_id.pae_den or '')
            year_id = year_minus_3
            hist_bloc_id = program_id.bloc_ids.filtered(lambda b: b.year_id == year_id)
            if not hist_bloc_id:
                # Try to find a bloc in another cycle for the given year
                hist_bloc_id = self.env['school.individual_bloc'].search([('student_id','=',bloc_id.student_id.id),('year_id','=',year_id.id)])
            if hist_bloc_id :
                hist_bloc_id = hist_bloc_id[0]
                sheet.write(i, 49, 'ETU')
                if self._is_dcc_bloc(hist_bloc_id) :
                    sheet.write(i, 50, 'DCC')
                elif hist_bloc_id.source_bloc_level == '1' :
                    sheet.write(i, 50, '1A1C')
                elif hist_bloc_id.source_bloc_level in ('2','3') :
                    sheet.write(i, 50, '>45')
                else:
                    sheet.write(i, 50, '1A2C')
                sheet.write(i, 51, program_id.track_id.saturn_code)
                sheet.write(i, 52, 'ESA')
                if hist_bloc_id.state in ('awarded_first_session','awarded_second_session'):
                    sheet.write(i, 53, 'R')
                else :
                    sheet.write(i, 53, 'E')
                sheet.write(i, 54, hist_bloc_id.total_acquiered_credits)
                sheet.write(i, 55, hist_bloc_id.total_credits)
            else :
                hist_id = self.env['school.student_annexe5_entry'].search([('year_id','=',year_id.id),('student_id','=',bloc_id.student_id.id)])
                if hist_id:
                    sheet.write(i, 49, hist_id.activite or '')
                    sheet.write(i, 50, hist_id.inscription or '')
                    sheet.write(i, 51, hist_id.code_saturn or '')
                    sheet.write(i, 52, hist_id.type or '')
                    sheet.write(i, 53, hist_id.resultat or '')
                    sheet.write(i, 54, hist_id.pae_num or '')
                    sheet.write(i, 55, hist_id.pae_den or '')
            year_id = year_minus_2
            hist_bloc_id = program_id.bloc_ids.filtered(lambda b: b.year_id == year_id)
            if not hist_bloc_id:
                # Try to find a bloc in another cycle for the given year
                hist_bloc_id = self.env['school.individual_bloc'].search([('student_id','=',bloc_id.student_id.id),('year_id','=',year_id.id)])
            if hist_bloc_id :
                hist_bloc_id = hist_bloc_id[0]
                sheet.write(i, 56, 'ETU')
                if self._is_dcc_bloc(hist_bloc_id) :
                    sheet.write(i, 57, 'DCC')
                elif hist_bloc_id.source_bloc_level == '1' :
                    sheet.write(i, 57, '1A1C')
                elif hist_bloc_id.source_bloc_level in ('2','3') :
                    sheet.write(i, 57, '>45')
                else:
                    sheet.write(i, 57, '1A2C')
                sheet.write(i, 58, program_id.track_id.saturn_code)
                sheet.write(i, 59, 'ESA')
                if hist_bloc_id.state in ('awarded_first_session','awarded_second_session'):
                    sheet.write(i, 60, 'R')
                else :
                    sheet.write(i, 60, 'E')
                sheet.write(i, 61, hist_bloc_id.total_acquiered_credits)
                sheet.write(i, 62, hist_bloc_id.total_credits)
            else :
                hist_id = self.env['school.student_annexe5_entry'].search([('year_id','=',year_id.id),('student_id','=',bloc_id.student_id.id)])
                if hist_id:
                    sheet.write(i, 56, hist_id.activite or '')
                    sheet.write(i, 57, hist_id.inscription or '')
                    sheet.write(i, 58, hist_id.code_saturn or '')
                    sheet.write(i, 59, hist_id.type or '')
                    sheet.write(i, 60, hist_id.resultat or '')
                    sheet.write(i, 61, hist_id.pae_num or '')
                    sheet.write(i, 62, hist_id.pae_den or '')
            year_id = year_minus_1
            hist_bloc_id = program_id.bloc_ids.filtered(lambda b: b.year_id == year_id)
            if not hist_bloc_id:
                # Try to find a bloc in another cycle for the given year
                hist_bloc_id = self.env['school.individual_bloc'].search([('student_id','=',bloc_id.student_id.id),('year_id','=',year_id.id)])
            if hist_bloc_id :
                hist_bloc_id = hist_bloc_id[0]
                sheet.write(i, 63, 'ETU')
                if self._is_dcc_bloc(hist_bloc_id) :
                    sheet.write(i, 64, 'DCC')
                elif hist_bloc_id.source_bloc_level == '1' :
                    sheet.write(i, 64, '1A1C')
                elif hist_bloc_id.source_bloc_level in ('2','3') :
                    sheet.write(i, 64, '>45')
                else:
                    sheet.write(i, 64, '1A2C')
                sheet.write(i, 65, program_id.track_id.saturn_code)
                sheet.write(i, 66, 'ESA')
                if hist_bloc_id.state in ('awarded_first_session','awarded_second_session'):
                    sheet.write(i, 67, 'R')
                else :
                    sheet.write(i, 67, 'E')
                sheet.write(i, 68, hist_bloc_id.total_acquiered_credits)
                sheet.write(i, 69, hist_bloc_id.total_credits)
            else :    
                hist_id = self.env['school.student_annexe5_entry'].search([('year_id','=',year_id.id),('student_id','=',bloc_id.student_id.id)])
                if hist_id:
                    sheet.write(i, 63, hist_id.activite or '')
                    sheet.write(i, 64, hist_id.inscription or '')
                    sheet.write(i, 65, hist_id.code_saturn or '')
                    sheet.write(i, 66, hist_id.type or '')
                    sheet.write(i, 67, hist_id.resultat or '')
                    sheet.write(i, 68, hist_id.pae_num or '')
                    sheet.write(i, 69, hist_id.pae_den or '')
            #sheet.write(i, 70, u'date inscription')
            #sheet.write(i, 76, u'REGULIER')
            #sheet.write(i, 77, u'IRREGULIER')
            #sheet.write(i, 78, u'FINANCABLE')
            #sheet.write(i, 79, u'NON FINANCABLE')
            #sheet.write(i, 80, u'PAE 16-17')
            #sheet.write(i, 81, u'A ENCODER SUR FICHIER SEPARE')
            #sheet.write(i, 82, u'A ENCODER SUR FICHIER SEPARE')
            sheet.write(i, 87, bloc_id.get_xml_id().get(bloc_id.id))
            sheet.write(i, 88, bloc_id.student_id.get_xml_id().get(bloc_id.student_id.id))
            sheet.write(i, 89, bloc_id.program_id.get_xml_id().get(bloc_id.program_id.id))
            i = i + 1

Annexe5Xlsx('report.school.annexe5.xlsx','school.saturn')