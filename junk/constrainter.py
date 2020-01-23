#!/usr/bin/env python3

import os
import fileinput
import subprocess
import json
import sys

def main():
    if not which('sourcekitten'):
        print('sourcekitten not installed, install with "brew install sourcekitten"')
        sys.exit(1)

    for (file_name, file_content) in get_input():
        constraints = parse_structure(file_to_json(file_content), file_content)
        write_to_file(file_name, file_content, constraints)

def translate_single(in_data):
    """

    >>> translate_single('NSLayoutConstraint(item: notificationIndicatorView, attribute: .bottom, relatedBy: .equal, toItem: self.underscoreTitleView, attribute: .top, multiplier: 1.0, constant: 0.0).isActive = true')
    'notificationIndicatorView.bottomAnchor.constraint(equalTo: self.underscoreTitleView.topAnchor)'
    >>> translate_single('NSLayoutConstraint(item: notificationIndicatorView, attribute: .bottom, relatedBy: .equal, toItem: self.underscoreTitleView, attribute: .top, multiplier: 1.0, constant: 1.0).isActive = true')
    'notificationIndicatorView.bottomAnchor.constraint(equalTo: self.underscoreTitleView.topAnchor, constant: 1.0)'
    >>> translate_single('NSLayoutConstraint(item: notificationIndicatorView, attribute: .bottom, relatedBy: .equal, toItem: self.underscoreTitleView, attribute: .top, multiplier: 0.5, constant: 0.0).isActive = true')
    >>> translate_single('NSLayoutConstraint(item: notificationIndicatorView, attribute: .width, relatedBy: .equal, toItem: nil, attribute: .notAnAttribute, multiplier: 1.0, constant: 35.0).isActive = true')
    'notificationIndicatorView.widthAnchor.constraint(equalToConstant: 35.0)'
    >>> translate_single('NSLayoutConstraint(item: titleLabel, attribute: .top, relatedBy: .equal, toItem: contentView, attribute: .top, multiplier: 1.0, constant: 18.0).isActive = true')
    'titleLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 18.0)'
    >>> translate_single('NSLayoutConstraint(item: titleLabel, attribute: .left, relatedBy: .equal, toItem: contentView, attribute: .left, multiplier: 1.0, constant: 18.0).isActive = true')
    'titleLabel.leftAnchor.constraint(equalTo: contentView.leftAnchor, constant: 18.0)'
    >>> translate_single('NSLayoutConstraint(item: titleLabel, attribute: .right, relatedBy: .equal, toItem: contentView, attribute: .right, multiplier: 1.0, constant: -18.0).isActive = true')
    'titleLabel.rightAnchor.constraint(equalTo: contentView.rightAnchor, constant: -18.0)'
    >>> translate_single('NSLayoutConstraint(item: downloadLabel, attribute: .left, relatedBy: .equal, toItem: contentView, attribute: .left, multiplier: 1.0, constant: 18.0).isActive = true')
    'downloadLabel.leftAnchor.constraint(equalTo: contentView.leftAnchor, constant: 18.0)'
    >>> translate_single('NSLayoutConstraint(item: downloadLabel, attribute: .top, relatedBy: .equal, toItem: titleLabel, attribute: .bottom, multiplier: 1.0, constant: 9.0).isActive = true')
    'downloadLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 9.0)'
    >>> translate_single('NSLayoutConstraint(item: downloadIcon, attribute: .right, relatedBy: .equal, toItem: contentView, attribute: .right, multiplier: 1.0, constant: -18.0).isActive = true')
    'downloadIcon.rightAnchor.constraint(equalTo: contentView.rightAnchor, constant: -18.0)'
    >>> translate_single('NSLayoutConstraint(item: downloadIcon, attribute: .bottom, relatedBy: .equal, toItem: downloadLabel, attribute: .bottom, multiplier: 1.0, constant: 0.0).isActive = true')
    'downloadIcon.bottomAnchor.constraint(equalTo: downloadLabel.bottomAnchor)'
    >>> translate_single('NSLayoutConstraint(item: progressBar, attribute: .top, relatedBy: .equal, toItem: downloadLabel, attribute: .bottom, multiplier: 1.0, constant: 9.0)')
    'progressBar.topAnchor.constraint(equalTo: downloadLabel.bottomAnchor, constant: 9.0)'
    >>> translate_single('NSLayoutConstraint(item: progressBar, attribute: .left, relatedBy: .equal, toItem: contentView, attribute: .left, multiplier: 1.0, constant: 18.0).isActive = true')
    'progressBar.leftAnchor.constraint(equalTo: contentView.leftAnchor, constant: 18.0)'
    >>> translate_single('NSLayoutConstraint(item: progressBar, attribute: .right, relatedBy: .equal, toItem: contentView, attribute: .right, multiplier: 1.0, constant: -18.0).isActive = true')
    'progressBar.rightAnchor.constraint(equalTo: contentView.rightAnchor, constant: -18.0)'
    >>> translate_single('NSLayoutConstraint(item: progressBar, attribute: .height, relatedBy: .equal, toItem: nil, attribute: .notAnAttribute, multiplier: 1.0, constant: 18.0)')
    'progressBar.heightAnchor.constraint(equalToConstant: 18.0)'
    >>> translate_single('NSLayoutConstraint(item: progressBar, attribute: .bottom, relatedBy: .equal, toItem: contentView, attribute: .bottom, multiplier: 1.0, constant: -18.0).isActive = true')
    'progressBar.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -18.0)'
    >>> translate_single('NSLayoutConstraint(item: titleLabel, attribute: .topMargin, relatedBy: .lessThanOrEqual, toItem: contentView, attribute: .bottomMargin, multiplier: 1.0, constant: 0.0)')
    'titleLabel.layoutMarginsGuide.topAnchor.constraint(lessThanOrEqualTo: contentView.layoutMarginsGuide.bottomAnchor)'
    """

    swift_json = file_to_json(in_data)
    constraints = parse_structure(swift_json, in_data.encode('utf-8'), True)
    return constraints[0].new_constraint() if len(constraints) > 0 else None


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def get_input():
    # map with 'filename' => 'content of that file'
    file_obj = {}

    for line in fileinput.input():
        if not fileinput.filename() in file_obj:
            file_obj[fileinput.filename()] = ""
        file_obj[fileinput.filename()] += line

    return { k: v.encode('utf-8') for k, v in file_obj.items() }.items()

def file_to_json(input_text):
    proc = subprocess.Popen(['sourcekitten', 'structure',  '--text', input_text],
            stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return json.loads(out.decode('utf-8'))

def parse_structure(structure, text_input, only_one=False):
    constraints = []
    if 'key.substructure' in structure:
        for item in structure['key.substructure']:
            if 'key.name' in item and item['key.name'] == 'NSLayoutConstraint':
                constraints.append(NSLayoutConstraint(item, text_input))
            constraints += parse_structure(item, text_input)
    return constraints

def write_to_file(file_name, file_content, constraints):
    with open(file_name, 'wb') as out:
        if len(constraints) == 0:
            out.write(file_content)
            return

        # Write from start -> first constraint
        out.write(file_content[0:constraints[0].offset])

        for (i, constraint) in enumerate(constraints):
            # Write constraint in anchor-form
            out.write(constraint.new_constraint().encode('utf-8'))

            if i == len(constraints) - 1:
                # this is last constraint, write end of last -> file end
                out.write(file_content[
                    constraint.offset + constraint.length: # from
                    len(file_content)                      # to
                ])
            else:
                # write from end of this constraint to beginning of next
                out.write(file_content[
                    constraint.offset + constraint.length: # from
                    constraints[i + 1].offset              # to
                ])


class NSLayoutConstraint:
    def __init__(self, structure, text_input):
        self.structure = structure
        self.text_input = text_input

        if type(text_input) != bytes:
            raise ValueError('Expecting input as `bytes`')

        self.offset = self.structure['key.offset']
        self.length = self.structure['key.length']
        self.body = text_input[self.offset:self.offset+self.length]

        for (i, arg) in enumerate(structure['key.substructure']):
            self.value_body_offset = arg['key.bodyoffset']
            self.value_body_length = arg['key.bodylength']
            self.value_body = text_input[self.value_body_offset:self.value_body_offset+self.value_body_length]

            # These are the arguments to the `NSLayoutConstraint` constructor
            # in iOS
            if i == 0:
                self.first_item = self.value_body.decode('utf-8')
            if i == 1:
                self.first_attribute = self.value_body.decode('utf-8')
            if i == 2:
                self.relation = self.value_body.decode('utf-8')
            if i == 3:
                self.second_item = self.value_body.decode('utf-8')
            if i == 4:
                self.second_attribute = self.value_body.decode('utf-8')
            if i == 5:
                self.multiplier = self.value_body.decode('utf-8')
            if i == 6:
                self.constant = self.value_body.decode('utf-8')

    def __str__(self):
        return self.body.decode('utf-8')

    def attribute_to_anchor(self, attribute):
        return {
            '.bottom': 'bottomAnchor',
            '.top': 'topAnchor',
            '.right': 'rightAnchor',
            '.left': 'leftAnchor',

            '.leading': 'leadingAnchor',
            '.trailing': 'trailingAnchor',

            '.centerX': 'centerXAnchor',
            '.centerY': 'centerYAnchor',

            '.leftMargin': 'layoutMarginsGuide.leftAnchor',
            '.rightMargin': 'layoutMarginsGuide.rightAnchor',
            '.topMargin': 'layoutMarginsGuide.topAnchor',
            '.bottomMargin': 'layoutMarginsGuide.bottomAnchor',

            '.leadingMargin': 'layoutMarginsGuide.leadingAnchor',
            '.trailingMargin': 'layoutMarginsGuide.trailingAnchor',

            '.centerXWithinMargins': 'layoutMarginsGuide.centerXAnchor',
            '.centerYWithinMargins': 'layoutMarginsGuide.centerYAnchor',

            '.firstBaseline': 'firstBaselineAnchor',
            '.lastBaseline': 'lastBaselineAnchor',

            '.height': 'heightAnchor',
            '.width': 'widthAnchor',

            '.notAnAttribute': None
        }[attribute]

    def relation_parameters_name(self, relation, constant=False):
        return {
            '.equal': 'equalToConstant' if constant else 'equalTo',
            '.lessThanOrEqual': 'lessThanOrEqualToConstant' if constant else 'lessThanOrEqualTo',
            '.greaterThanOrEqual': 'greaterThanOrEqualToConstant' if constant else 'greaterThanOrEqualTo'
        }[relation]

    def constant_part(self):
        try:
            # if self.contant == 0, means it doesnt make any difference
            # so we can remove it
            if float(self.constant) == 0:
                return None
        except ValueError:
            pass
        return self.constant

    def multiplier_part(self):
        try:
            # self.multiplier == 1 means it doesnt contribute to layout
            # so we can remove it
            if float(self.multiplier) == 1:
                return None
        except ValueError:
            pass

        if self.first_attribute != '.height' and self.first_attribute != '.width':
            raise ValueError("Multiplier only works for heigh & width, see NSLayoutDimension")

        return self.multiplier

    def new_constraint(self):
        first_attribute = self.attribute_to_anchor(self.first_attribute)
        second_attribute = self.attribute_to_anchor(self.second_attribute)

        if first_attribute and second_attribute:
            # This is for these functions:
            #
            # open func constraint(equalTo anchor: NSLayoutAnchor<AnchorType>) -> NSLayoutConstraint
            # open func constraint(greaterThanOrEqualTo anchor: NSLayoutAnchor<AnchorType>) -> NSLayoutConstraint
            # open func constraint(lessThanOrEqualTo anchor: NSLayoutAnchor<AnchorType>) -> NSLayoutConstraint
            #
            # open func constraint(equalTo anchor: NSLayoutAnchor<AnchorType>, constant c: CGFloat) -> NSLayoutConstraint
            # open func constraint(greaterThanOrEqualTo anchor: NSLayoutAnchor<AnchorType>, constant c: CGFloat) -> NSLayoutConstraint
            # open func constraint(lessThanOrEqualTo anchor: NSLayoutAnchor<AnchorType>, constant c: CGFloat) -> NSLayoutConstraint
            #
            # open func constraint(equalTo anchor: NSLayoutDimension, multiplier m: CGFloat) -> NSLayoutConstraint
            # open func constraint(greaterThanOrEqualTo anchor: NSLayoutDimension, multiplier m: CGFloat) -> NSLayoutConstraint
            # open func constraint(lessThanOrEqualTo anchor: NSLayoutDimension, multiplier m: CGFloat) -> NSLayoutConstraint

            # open func constraint(equalTo anchor: NSLayoutDimension, multiplier m: CGFloat, constant c: CGFloat) -> NSLayoutConstraint
            # open func constraint(greaterThanOrEqualTo anchor: NSLayoutDimension, multiplier m: CGFloat, constant c: CGFloat) -> NSLayoutConstraint
            # open func constraint(lessThanOrEqualTo anchor: NSLayoutDimension, multiplier m: CGFloat, constant c: CGFloat) -> NSLayoutConstraint

            ret = "%s.%s.constraint(%s: %s.%s" % (
                self.first_item,
                first_attribute,
                self.relation_parameters_name(self.relation),
                self.second_item,
                second_attribute
            )

            try:
                multiplier = self.multiplier_part()
                if multiplier:
                    ret += ", multiplier: %s" % multiplier
            except:
                return None

            constant = self.constant_part()
            if constant:
                ret += ", constant: %s" % constant

            ret += ")"

        elif first_attribute:
            # This for these functions:
            #
            # open func constraint(equalToConstant c: CGFloat) -> NSLayoutConstraint
            # open func constraint(greaterThanOrEqualToConstant c: CGFloat) -> NSLayoutConstraint
            # open func constraint(lessThanOrEqualToConstant c: CGFloat) -> NSLayoutConstraint

            ret = "%s.%s.constraint(%s: %s)" % (
                self.first_item,
                first_attribute,
                self.relation_parameters_name(self.relation, True),
                self.constant_part()
            )

        return ret

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        import doctest
        doctest.testmod()
        sys.exit(0)
    main()
    sys.exit(0)
