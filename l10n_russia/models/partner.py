# -*- coding: utf-8 -*-
from re import fullmatch

from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    psrn = fields.Char(
        string="PSRN",
        help="Primary State Registration Number"
        "\nContains 13 digits. First one: 1,5 - for commercial organizations"
        "\nThe rest except 3 - for state agencies.",
        index=True,
    )
    iec = fields.Char(
        string="IEC",
        help="Industrial Enterprises Classifier"
        "Have 9 numbers length"
        "\nNumbers 5, 6 are 01-50 for russian companies and 51-99 for foreign companies.",
        index=True,
    )
    okpo = fields.Char(
        string="ARCEO",
        help="All-Russian Classifier of Enterprises and Organizations"
        "\nContains 8 digits for companies or 10 digits for sole proprietors.",
        index=True,
    )
    arceat = fields.Char(
        string="Main code ARCEAT",
        help="All-Russian classifier of economic activity types, Main code for company"
        "\nFormat: 00.00 or 00.00.0 or 00.00.00",
    )
    company_form = fields.Selection(
        selection=[
            ("sp", "Sole Proprietor"),
            ("pshp", "Partnership"),
            ("coop", "Cooperative"),
            ("plc", "Private Limited Company"),
            ("jsc", "Joint stock company"),
            ("pc", "Public company"),
            ("ga", "Government agency"),
            ("сjsc", "Сlosed joint stock company"),
        ],
        string="Institutional-Legal Form",
        default="plc",
    )
    psrn_sp = fields.Char(
        string="PSRN SP",
        help="Primary State Registration Number of Sole Proprietorship"
        "\nContains 15 digits. First digit should be 3",
    )
    sp_register_number = fields.Char(
        string="SP Certificate Number",
        help="SP registration certificate number. " "Since 28.04.2018 not necessary",
    )

    sp_register_date = fields.Date(
        string="SP Registration Date",
        help="SP registration certificate date" "Since 28.04.2018 not necessary",
    )
    passport_number = fields.Char(
        string="Passport №", help="Passport series and number", index=True
    )
    passport_department = fields.Char(
        string="Passport issued by", help="Department issued the passport"
    )
    passport_date = fields.Date(
        string="Passport issue date", help="Passport issue date"
    )
    birth_date = fields.Date(string="Birth date", help="Person's birth date")

    @api.constrains("is_company")
    def _check_company_form_fill(self):
        if self.filtered(lambda r: r.is_company and not r.company_form):
            raise ValidationError(_("Institutional-Legal Form must be set up!"))

    @api.constrains("vat", "is_company", "company_form", "country_id")
    def _check_tin(self):
        """
        Validates russian TIN.
        The russian TIN is a unique number which consists of 10 numbers for
        organizations and of 12 numbers for persons and sole proprietors.
        Uniqueness check for TIN value is a standard Odoo feature,
        and realized in base module.
        """
        for partner_rec in self:
            vat_regex = r"[0-9]{%s}" % (
                "10"
                if partner_rec.is_company and partner_rec.company_form != "sp"
                else "12"
            )
            if (
                partner_rec.vat
                and partner_rec.country_id.code == "RU"
                and not partner_rec.parent_id
                and not fullmatch(vat_regex, partner_rec.vat)
            ):
                raise ValidationError(
                    _(
                        "TIN for partner %s is incorrect. Please check the TIN data and the company/individual setting."
                        % partner_rec.name
                    )
                )

    @api.constrains("iec", "is_company", "company_form", "country_id")
    def _check_iec(self):
        """
        Validates IEC.
        The IEC have 9 numbers length. 5,6 numbers are 01-50 for russian companies
        and 51-99 for foreign companies.
        Companies only can have IEC, not sole proprietors or individuals.
        """
        iec_regex = r"[0-9]{9}"
        for partner_rec in self:
            if (
                partner_rec.is_company
                and partner_rec.company_form != "sp"
                and partner_rec.iec
                and not fullmatch(iec_regex, partner_rec.iec)
            ):
                raise ValidationError(
                    _("IEC is incorrect. Please check the IEC and country data")
                )
            if (
                partner_rec.is_company
                and partner_rec.company_form != "sp"
                and partner_rec.iec
                and partner_rec.country_id
                and (
                    1 <= int(partner_rec.iec[4:6]) <= 50
                    and partner_rec.country_id.code != "RU"
                    or 51 <= int(partner_rec.iec[4:6]) <= 99
                    and partner_rec.country_id.code == "RU"
                )
            ):
                raise ValidationError(
                    _(
                        "5,6 symbols of IEC are incorrect. Please check the IEC and country data."
                    )
                )

    @api.constrains("okpo", "is_company", "company_form", "country_id")
    def _check_okpo(self):
        """
        Validates ARCEO.
        ARCEO is unique, contains 8 digits for companies or 10 digits for
        sole proprietors.
        """
        for partner_rec in self:
            okpo_regex = r"[0-9]{%s}" % (
                "10" if partner_rec.company_form == "sp" else "8"
            )
            if (
                partner_rec.is_company
                and partner_rec.okpo
                and not fullmatch(okpo_regex, partner_rec.okpo)
            ):
                raise ValidationError(_("ARCEO is incorrect. Please check the data."))

            if partner_rec.is_company and partner_rec.okpo:
                partner_exist = self.env["res.partner"].search(
                    [("is_company", "=", True), ("okpo", "=", partner_rec.okpo)]
                )
                partner_names = [
                    partner.name
                    for partner in partner_exist
                    if partner.id != partner_rec.id
                ]
                if partner_exist and (
                    len(partner_exist) > 1 or partner_exist.id != partner_rec.id
                ):
                    raise ValidationError(
                        _('Partner with ARCEO "%s" already exists (%s)')
                        % (partner_rec.okpo, ", ".join(partner_names))
                    )

    @api.constrains("arceat", "is_company", "company_form", "country_id")
    def _check_arceat(self):
        """
        Validates ARCEAT main code. It's format: 00.00.00 or 00.00.0 or 00.00
        Code not unique
        """
        arceat_regex = r"[0-9]{2}\.[0-9]{2}(?:\.[1-9]{,2})?"
        for partner_rec in self:
            if (
                partner_rec.is_company
                and partner_rec.arceat
                and not fullmatch(arceat_regex, partner_rec.arceat)
            ):
                raise ValidationError(
                    _(
                        'Wrong ARCEAT code format.\nIt should contain digits only and be like "00.00" or "00.00.0", or "00.00.00"'
                    )
                )

    @api.constrains("psrn", "is_company", "company_form", "country_id")
    def _check_psrn(self):
        """
        Validates PSRN.
        PSRN is unique, contains 13 digits. First digit for companies is one of these:
         1, 5 - for commercial organizations; 2, 4, 6, 7, 8, 9 - for state agencies.
        """
        for partner_rec in self:
            psrn_regex = r"[0-9]{13}"
            if (
                partner_rec.is_company
                and partner_rec.psrn
                and not fullmatch(psrn_regex, partner_rec.psrn)
            ):
                raise ValidationError(_("PSRN is incorrect. Please check the data"))

            if partner_rec.is_company and partner_rec.psrn:
                partner_exist = self.env["res.partner"].search(
                    [("is_company", "=", True), ("psrn", "=", partner_rec.psrn)]
                )
                partner_names = [
                    partner.name
                    for partner in partner_exist
                    if partner.id != partner_rec.id
                ]
                if partner_exist and (
                    len(partner_exist) > 1 or partner_exist.id != partner_rec.id
                ):
                    raise ValidationError(
                        _('Partner with PSRN "%s" already exists (%s)')
                        % (partner_rec.psrn, ", ".join(partner_names))
                    )

            if partner_rec.psrn and (
                (
                    int(partner_rec.psrn[0]) in (1, 5)
                    and partner_rec.company_form in ("sp", "ga")
                )
                or (
                    int(partner_rec.psrn[0]) not in (1, 3, 5)
                    and partner_rec.company_form not in ("sp", "ga")
                )
                or int(partner_rec.psrn[0]) == 3
            ):
                raise ValidationError(_("First PSRN symbol mismatch company form."))

    @api.constrains("psrn_sp", "is_company", "company_form", "country_id")
    def _check_psrn_sp(self):
        """
        Validates PSRN SP.
        PSRN SP is unique, contains 15 digits. First digit should be 3
        """
        for partner_rec in self:
            psrn_sp_regex = r"[0-9]{15}"
            if (
                partner_rec.is_company
                and partner_rec.psrn_sp
                and not fullmatch(psrn_sp_regex, partner_rec.psrn_sp)
            ):
                raise ValidationError(_("PSRN SP is incorrect. Please check the data"))

            if partner_rec.is_company and partner_rec.psrn_sp:
                partner_exist = self.env["res.partner"].search(
                    [("is_company", "=", True), ("psrn_sp", "=", partner_rec.psrn_sp)]
                )
                partner_names = [
                    partner.name
                    for partner in partner_exist
                    if partner.id != partner_rec.id
                ]
                if partner_exist and (
                    len(partner_exist) > 1 or partner_exist.id != partner_rec.id
                ):
                    raise ValidationError(
                        _('Partner with PSRN SP "%s" already exists (%s)')
                        % (partner_rec.psrn_sp, ", ".join(partner_names))
                    )

            if partner_rec.psrn_sp and int(partner_rec.psrn_sp[0]) != 3:
                raise ValidationError(_("First PSRN SP symbol mismatch company form."))
