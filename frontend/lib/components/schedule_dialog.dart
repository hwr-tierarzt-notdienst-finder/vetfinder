import 'package:flutter/material.dart';
import 'package:easy_localization/easy_localization.dart';

class ScheduleDialog extends StatelessWidget {
  const ScheduleDialog({super.key});

  @override
  Widget build(BuildContext context) {
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
        child: Column()
      ),
    );
  }
}