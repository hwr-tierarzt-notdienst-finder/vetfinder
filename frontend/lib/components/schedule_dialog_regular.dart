import 'package:flutter/material.dart';
import 'package:easy_localization/easy_localization.dart';

import 'package:frontend/utils/constants.dart';
import 'package:frontend/api.dart';

class ScheduleDialogRegular extends StatelessWidget {
  const ScheduleDialogRegular({
    Key? key,
    required this.id,
  }) : super(key: key);

  final String id;

  @override
  Widget build(BuildContext context) {
    Veterinarian currentVet = getVeterinarianById(id);

    return AlertDialog(
      title: Text('schedule_dialog.title'.tr()),
      contentPadding: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
      ),
      actions: <Widget>[
        TextButton(
          style: TextButton.styleFrom(
            textStyle: Theme.of(context).textTheme.labelLarge,
          ),
          child: Text('schedule_dialog.close'.tr()),
          onPressed: () {
            Navigator.of(context).pop();
          },
        ),
      ],
      content: Container(
        padding: const EdgeInsets.symmetric(horizontal: 25),
        width: MediaQuery.of(context).size.width * 0.75,
        height: MediaQuery.of(context).size.height * 0.5,
        child: Container(
          width: MediaQuery.of(context).size.width * 0.75,
          height: MediaQuery.of(context).size.height * 0.5,
          child: Container(
            margin: const EdgeInsets.only(top: 10),
            child: DataTable(
              headingRowHeight: 0,
              columns: const [
                DataColumn(label: Text("")),
                DataColumn(label: Text("")),
              ],
              rows: [
                DataRow(cells: [
                  DataCell(Text("schedule_dialog.monday".tr())),
                  DataCell(
                      Text(currentVet.getAvailabilityDuringWeek(daysMon))),
                ]),
                DataRow(cells: [
                  DataCell(Text("schedule_dialog.tuesday".tr())),
                  DataCell(
                      Text(currentVet.getAvailabilityDuringWeek(daysTue))),
                ]),
                DataRow(cells: [
                  DataCell(Text("schedule_dialog.wednesday".tr())),
                  DataCell(
                      Text(currentVet.getAvailabilityDuringWeek(daysWed))),
                ]),
                DataRow(cells: [
                  DataCell(Text("schedule_dialog.thursday".tr())),
                  DataCell(
                      Text(currentVet.getAvailabilityDuringWeek(daysThu))),
                ]),
                DataRow(cells: [
                  DataCell(Text("schedule_dialog.friday".tr())),
                  DataCell(
                      Text(currentVet.getAvailabilityDuringWeek(daysFri))),
                ]),
                DataRow(cells: [
                  DataCell(Text("schedule_dialog.saturday".tr())),
                  DataCell(
                      Text(currentVet.getAvailabilityDuringWeek(daysSat))),
                ]),
                DataRow(cells: [
                  DataCell(Text("schedule_dialog.sunday".tr())),
                  DataCell(
                      Text(currentVet.getAvailabilityDuringWeek(daysSun))),
                ]),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
